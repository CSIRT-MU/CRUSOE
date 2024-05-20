import { Injectable } from '@angular/core';
import { comparator_config } from '../config/comparator_config';
import { forgetCache } from '@apollo/client/cache/inmemory/reactiveVars';
@Injectable({
  providedIn: 'root',
})
export class ComparatorService {
  private config;
  private osConfig;
  private osWeights = [];
  private antivirusConfig;
  private antivirusWeights = [];
  private networkServicesConfig;
  private cmsConfig;
  private cmsWeights;
  private total_cve_count;
  private total_event_count;

  public threshold = 0;
  constructor(cve_count: number, event_count: number) {
    this.config = comparator_config.comparators;
    this.osConfig = this.config.os;
    this.osWeights = [this.osConfig.vendor, this.osConfig.product, this.osConfig.version];
    this.antivirusConfig = this.config.antivirus;
    this.antivirusWeights = [this.antivirusConfig.vendor, this.antivirusConfig.product, this.antivirusConfig.version];
    this.cmsConfig = this.config.cms;
    this.cmsWeights = [this.cmsConfig.vendor, this.cmsConfig.product, this.cmsConfig.version];
    this.networkServicesConfig = this.config.net_service;
    this.threshold = this.calculateThreshold();
    this.total_cve_count = cve_count;
    this.total_event_count = event_count;
  }

  private calculateThreshold(): number {
    let result = 1;
    for (const comparator in this.config) {
      if (this.config[comparator].apply) {
        result *= this.config[comparator].critical_bound;
      }
    }
    return result;
  }

  public calculateRiskScore(from: any, to: any) {
    let similarity = 1.0;

    if (this.osConfig.apply) {
      similarity *= this.OsComparator(from.nodes[0]?.is_a[0]?.os, to.nodes[0]?.is_a[0]?.os);
    }

    if (this.antivirusConfig.apply) {
      similarity *= this.AntivirusComparator(from.nodes[0]?.is_a[0]?.antivirus, to.nodes[0]?.is_a[0]?.antivirus);
    }

    if (this.config.cve_cumulative.apply) {
      similarity *= this.CveComparator(from.nodes[0]?.is_a[0], to.nodes[0]?.is_a[0]);
    }

    if (this.config.event_cumulative.apply) {
      similarity *= this.EventComparator(from.source_of, to.source_of);
    }

    if (this.networkServicesConfig.apply) {
      similarity *= this.NetServicesComparator(
        from.nodes[0]?.is_a[0]?.networkservices,
        to.nodes[0]?.is_a[0]?.networkservices
      );
    }

    if (this.cmsConfig.apply) {
      similarity *= this.CmsComparator(from.nodes[0]?.is_a[0], to.nodes[0]?.is_a[0]);
    }

    return similarity;
  }

  private OsComparator(from: any, to: any): number {
    if (from === undefined && to === undefined) return 1;
    if (from === undefined || to === undefined) return this.osConfig.diff_value;
    if (from.length === 0 && to.length === 0) return 1;
    if (from.length === 0 || to.length === 0) return this.osConfig.diff_value;

    const cpe1 = from[0].version.split(':');
    const cpe2 = to[0].version.split(':');

    let result_similarity = 0;
    for (let i = 0; i < Math.min(cpe1.length, cpe2.length); i++) {
      if (this.compareCpeParts(cpe1[i], cpe2[i])) {
        result_similarity += this.osWeights[i];
      }
    }
    return result_similarity;
  }

  private AntivirusComparator(from: any, to: any): number {
    if (from === undefined && to === undefined) return 1;
    if (from === undefined || to === undefined) return this.antivirusConfig.diff_value;
    if (from.length === 0 && to.length === 0) return 1;
    if (from.length === 0 || to.length === 0) return this.antivirusConfig.diff_value;

    const cpe1 = from[0].version.split(':');
    const cpe2 = to[0].version.split(':');

    let result_similarity = 0;
    for (let i = 0; i < Math.min(cpe1.length, cpe2.length); i++) {
      if (this.compareCpeParts(cpe1[i], cpe2[i])) {
        result_similarity += this.antivirusWeights[i];
      }
    }
    return result_similarity;
  }

  private CveComparator(from: any, to: any): number {
    const fromCount = this.getHostCveCount(from);
    const toCount = this.getHostCveCount(to);

    return this.calculateCumulativeSimilarity(fromCount, toCount, this.total_cve_count);
  }

  private getHostCveCount(host: any): number {
    if (host === undefined) return 0;
    let total = 0;
    if (host.os.length !== 0) total += host.os[0].vulnerabilitys.length;
    if (host.antivirus.length !== 0) total += host.antivirus[0].vulnerabilitys.length;

    return total;
  }

  private EventComparator(from: any, to: any): number {
    const fromCount = from.length;
    const toCount = to.length;

    return this.calculateCumulativeSimilarity(fromCount, toCount, this.total_event_count);
  }

  private calculateCumulativeSimilarity(n1: number, n2: number, total: number): number {
    const average = (n1 + n2) / 2.0;

    if (average === 0) return 1.0 / total;
    if (total === 0) return 1.0;

    return average / total;
  }

  private CmsComparator(from: any, to: any): number {
    if (from === undefined && to === undefined) return 1;
    if (from === undefined || to === undefined) return this.cmsConfig.diff_value;

    if (this.cmsConfig.require_open_ports) {
      if (this.checkHttpPort(from.networkservices) !== this.checkHttpPort(to.networkservices))
        return this.cmsConfig.diff_value;
      if (!this.checkHttpPort(from.networkservices)) return 1;
    }

    if (from.cms.length === 0 && to.cms.length === 0) return 1;
    if (from.cms.length === 0 || to.cms.length === 0) return this.osConfig.diff_value;

    const cpe1 = from.cms[0].version.split(':');
    const cpe2 = to.cms[0].version.split(':');

    let result_similarity = 0;
    for (let i = 0; i < Math.min(cpe1.length, cpe2.length); i++) {
      if (this.compareCpeParts(cpe1[i], cpe2[i])) {
        result_similarity += this.cmsWeights[i];
      }
    }
    return result_similarity;
  }

  private checkHttpPort(service: any): boolean {
    if (service.protocol === 'TCP' && (service.port === 80 || service.port === 443)) return true;
    return false;
  }

  private NetServicesComparator(from: any, to: any): number {
    if (from === undefined && to === undefined) return 1;
    if (from === undefined || to === undefined) return this.networkServicesConfig.diff_value;
    if (from.length === 0 && to.length === 0) return 1;

    let i1 = 0;
    let i2 = 0;
    let same_service_count = 0;

    from = this.sortNetworkServices(from);
    to = this.sortNetworkServices(to);

    while (i1 < from.length && i2 < to.length) {
      if (from[i1].port === to[i2].port && from[i1].protocol === to[i2].protocol) {
        same_service_count += 1;
        i1 += 1;
        i2 += 1;
      } else if (from[i1].protocol > to[i2].protocol || from[i1].port > to[i2].port) {
        i2 += 1;
      } else {
        i1 += 1;
      }

      if (same_service_count === 0) {
        return this.networkServicesConfig.diff_value;
      }

      return same_service_count / (from.length + to.length - same_service_count);
    }
  }

  private sortNetworkServices(services: any): any {
    return services.slice().sort((serviceA, serviceB) => {
      return serviceA.protocol.localeCompare(serviceB.protocol) || serviceA.port - serviceB.port;
    });
  }

  private compareCpeParts(part1: string, part2: string): boolean {
    return part1 === part2 || part1 === '*' || part2 === '*';
  }
}
