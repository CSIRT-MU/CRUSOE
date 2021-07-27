import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Pao, PaoResponse } from '../../models/pao.model';
import { DecideService } from '../../decideact.service';

@Component({
  selector: 'app-pao',
  templateUrl: './pao.component.html',
  styleUrls: ['./pao.component.scss'],
})
export class PaoComponent implements OnInit {
  pao: Pao;
  paoLoading = true;

  constructor(private route: ActivatedRoute, private decide: DecideService) {
    const name = this.route.snapshot.params.name;
    this.decide.getPaos().subscribe((paos: PaoResponse) => {
      this.pao = paos.paos.find((p: Pao) => p.pao === name);
      this.paoLoading = false;
    });
  }

  ngOnInit(): void {}
}
