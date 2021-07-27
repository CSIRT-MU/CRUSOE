from datetime import timedelta, datetime
from flowmonclient import FmcClient
from paramiko import RSAKey, SSHClient, AutoAddPolicy
from json import dumps
import csv
import re
import os
import structlog


def round_time(time):
    """
    Get time of last flowmon export.
    :param time: current time.
    :return: rounded time.
    """
    t_min = time.minute % 5
    t_sec = time.second
    t_mic = time.microsecond
    time = time - timedelta(minutes=t_min, seconds=t_sec, microseconds=t_mic)
    return time


def is_valid(line):
    """
    Check whether given line has valid format
    :param line: checked line(string)
    :return: True if valid, false otherwise
    """
    return ('tcpwinsize' not in line
            or (line['tcpwinsize'].isdigit() and line['tcpttl'].isdigit() and line['tcpsynsize'].isdigit())
            or (line['tcpwinsize'] == 'N/A' and line['tcpttl'] == 'N/A' and line['tcpsynsize'] == 'N/A'))


def clean(line):
    """
    Extract elements from line, add fixed format
    :param line: checked line(string)
    :return: String with elements
    """
    result = ''
    for element in line.split(';'):
        result += element.strip(' ') + ';'
    if result[0] == ';':
        result = result[1:]
    return result[:-3] + '\n'


def download_ssh(
        user='',
        password='',
        hostname='',
        nfdump_path='',
        dir_param='',
        collectors=[],
        m_time=None,
        aggregate='',
        flow_filter='',
        output_format='',
        remote_file_path='',
        local_tmp_path='',
        key_path='',
        logger=structlog.get_logger()):
    """
    Download data from flowmon using ssh
    :param user: ssh user
    :param password: ssh password
    :param hostname: ssh hostname
    :param nfdump_path: local nfdump path
    :param dir_param: Directory nfdump params (i.e. -M)
    :param collectors: list of collectors
    :param m_time: modification time
    :param aggregate: nfdump aggregation filters (i.e. -A)
    :param flow_filter: nfdump flow filters (i.e. "src net...")
    :param output_format: nfdump output format (i.e. -O)
    :param remote_file_path: path to remote file
    :param local_tmp_path: local tmp path
    :param key_path: path to ssh key
    :param logger: logger instance
    :return:
    """

    if m_time is None:
        m_time = round_time(datetime.now() - timedelta(minutes=5))

    k = RSAKey.from_private_key_file(key_path, password=password)
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    logger.info("Connecting ... \t" + hostname)
    ssh_client.connect(hostname=hostname, username=user, pkey=k)

    dir_path = m_time.strftime('%Y/%m/%d/')
    file_name = 'nfcapd.' + m_time.strftime('%Y%m%d%H%M')
    for collector in collectors:
        dir_param = f"{dir_param}{collector}:"
    dir_param = dir_param[:-1]
    nfdump_file_params = f" -r {dir_path}{file_name}"
    command = f"{nfdump_path} {dir_param}{nfdump_file_params} {aggregate} {flow_filter} {output_format}   > {remote_file_path}"
    print(command)
    logger.info("Executing ... \t" + command)
    # return ''
    stdin, stdout, stderr = ssh_client.exec_command(command)
    if str(stderr.read()) != 'b\'\'':
        logger.error(stderr.read())

    local_dir = local_tmp_path[:local_tmp_path.rindex("/")]
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    localpath = f"{local_tmp_path}{dir_path.replace('/', '')}{file_name[15:19]}"

    logger.info("Downloading ...\t" + remote_file_path)
    sftp = ssh_client.open_sftp()
    sftp.get(remote_file_path, localpath + '.csv~')
    sftp.close()
    ssh_client.close()

    logger.info("Writing ... \t" + localpath)

    fieldnames = re.findall('(?<=%)[^;]*', output_format)
    header_len = len(fieldnames)

    with open(localpath + '.csv~', 'r', encoding="ISO-8859-1") as rawcsv:
        with open(localpath + '.csv', 'w', encoding="ISO-8859-1") as finalcsv:
            for line in rawcsv:
                if line.count(';') == header_len:
                    finalcsv.write(clean(line))
    counter = 0
    with open(localpath + '.csv', 'r', encoding="ISO-8859-1") as csvfile:
        with open(localpath + '.json', 'w', encoding="ISO-8859-1") as jsonfile:
            reader = csv.DictReader(csvfile, fieldnames, delimiter=';')
            jsonfile.write('[')
            for row in reader:
                if is_valid(row):
                    jsonfile.write(f'{dumps(row)},\n')
                    counter += 1
                else:
                    logger.warning(f"invalid flow: {line}")
            jsonfile.write('{}]')

    logger.info('Disconnected \t' + hostname)

    return localpath + '.json', counter


def download_rest(
        domain='https://collector2.csirt.muni.cz',
        username='rest',
        from_time=None,
        to_time=None,
        profile='CSIRTM-51b615',
        channels=['ICSFI-87e3958'],
        filter='src net 147.251.0.0/16 and not dst net 147.251.0.0/16',
        output=None,
        output_file=None,
        password=None,
        logger=structlog.get_logger()):
    """
    :param output:
    :param output_file: path to output file
    :param logger: logger instance
    :param from_time: start time from which download will be done
    :param domain: for access to rest
    :param username: for access to rest
    :param password: for access to rest
    :param to_time: actual time or time which we want analyse
    :param profile: which we want use
    :param channels: list of channels we want use
    :param filter: filter out uninteresting data
    :return: flows result of query
    """

    if to_time is None:
        to_time = datetime.now()

    if from_time is None:
        from_time = to_time - timedelta(minutes=5)

    flowmon = FmcClient(domain=domain, username=username, password=password)

    raw_analyse = flowmon.analysis.flows(
        showonly=10000,
        profile=profile,
        channels=channels,
        output=output,
        from_timestamp=from_time,
        to_timestamp=to_time,
        filter=filter)

    flow_id = raw_analyse['id']
    flow = flowmon.analysis.results(flow_id)

    with open(output_file, 'w') as ofile:
        ofile.write(dumps(flow))

    return "Parsed {len(flow)} flows"
