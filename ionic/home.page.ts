import { Component } from '@angular/core';
import { ApiService } from '../api.service';

interface SearchResult {
  sentences?: string[];
  text?: string;
  citations?: {[key: string]: number}[];
  top_citations?: {[key: string]: number}[];
}


@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage {
  result?: SearchResult;
  query: string = '';
  clean: boolean = false;
  showSources: boolean = false;

  constructor(private apiService: ApiService) {}

  search() {
    this.apiService.search(this.query, this.clean, this.showSources).subscribe(
      data => {
        console.log("Data set to result:", data);
        this.result = data;
      },
      error => {
        console.error('Error fetching data: ', error);
      }
    );
  }
}

