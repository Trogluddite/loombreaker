import { Component } from '@angular/core';
import { MarkovService } from '/api/markov.service';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage {
  markovData: any;

  constructor(private markovService: MarkovService) {}

  ngOnInit() {
    this.markovService.getMarkovData().subscribe(data => {
      this.markovData = data;
    });
  }
}
