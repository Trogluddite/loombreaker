import { Component } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage {
  query: string = '';
  results: any[] = [];

  constructor(private apiService: ApiService) {}

  search() {
    this.apiService.search(this.query).subscribe(
      data => {
        this.results = data.sentences; // Assuming the response has a 'sentences' property
      },
      error => {
        console.error('Error fetching data: ', error);
      }
    );
  }
}

