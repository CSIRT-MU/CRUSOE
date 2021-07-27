"""OS identification method using netflows -- User-Agent

This module contains implementation of UserAgent class which is a method for OS
identification using User-Agent technique.
"""
import structlog

class UserAgent:
    """UserAgent OS identification technique

    This class provides an interface for performing OS identification based on
    netflow data.
    """

    WIN_MAP = {'Windows 10.0': 'Windows 10',
               'Windows 6.3': 'Windows 8.1',
               'Windows 6.2': 'Windows 8',
               'Windows 6.1': 'Windows 7',
               'Windows 6.0': 'Windows Vista',
               'Windows 5.2': 'Windows XP Professional x64',
               'Windows 5.1': 'Windows XP',
               'Windows 5.0': 'Windows 2000'}

    API_MAP = {#'Android 1': 'Android 1.0',
               #'Android 2': 'Android 1.1',
               #'Android 3': 'Android 1.5',
               #'Android 4': 'Android 1.6',
               #'Android 5': 'Android 2.0',
               #'Android 6': 'Android 2.0',
               #'Android 7': 'Android 2.1',
               #'Android 8': 'Android 2.2.x',
               #'Android 9': 'Android 2.3',
               'Android 10': 'Android 2.3',
               'Android 11': 'Android 3.0',
               'Android 12': 'Android 3.1',
               'Android 13': 'Android 3.2',
               'Android 14': 'Android 4.0',
               'Android 15': 'Android 4.0',
               'Android 16': 'Android 4.1',
               'Android 17': 'Android 4.2',
               'Android 18': 'Android 4.3',
               'Android 19': 'Android 4.4',
               'Android 21': 'Android 5.0',
               'Android 22': 'Android 5.1',
               'Android 23': 'Android 6.0',
               'Android 24': 'Android 7.0',
               'Android 25': 'Android 7.1',
               'Android 26': 'Android 8.0',
               'Android 27': 'Android 8.1',
               'Android 28': 'Android 9'}

    @classmethod
    def convert_win(cls, os_name):
        """
        Convert windows version to windows name
        :param os: windows version
        :return: windows name
        """
        return cls.WIN_MAP.get(os_name, os_name)

    @classmethod
    def convert_api(cls, os_name):
        """
        Convert Android API version to OS version
        :param os: Android string with API version
        :return: Android sring with OS version
        """
        return cls.API_MAP.get(os_name, os_name)

    def __init__(self, logger=structlog.get_logger()):
        self.logger = logger.bind(method="useragent")

    def run(self, flows):
        """Run the method on given flows
        :param flows: flows to process
        :return: dictionary between IPs and predicted operating systems
        """
        self.logger.info("Method start")

        result = {}
        for flow in flows:
            try:
                if "sa" not in flow:
                    continue
                sa = flow["sa"]
                os_name = flow["hos"]
                major = flow["hosmaj"]
                minor = flow["hosmin"]

                tmp = result.get(sa, {})

                if os_name != "N/A":
                    if major != "N/A":
                        os_name += " " + major
                        if minor != "N/A":
                            os_name += "." + minor

                    os_name = self.convert_win(os_name)
                    os_name = self.convert_api(os_name)
                    tmp[os_name] = tmp.get(os_name, 0) + 1

                if tmp:
                    result[sa] = tmp

            except KeyError as e:
                self.logger.warning('Flow is missing a necessary key!', key=str(e))
            except Exception as e:
                self.logger.warning(f'Exception while processing flow!', exception=str(e), flow=str(flow))

        for sa in result:
            total = sum(result[sa].values())
            for os_name in result[sa].keys():
                result[sa][os_name] /= total

        self.logger.info("Method finish")

        return result
