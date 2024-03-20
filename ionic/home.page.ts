import { Component } from '@angular/core';
import { DataService } from '/api/480Project/data.service';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage {
  query: string = '';
  cats: any[] = [];

  constructor(private dataService: DataService) { }
  
  searchForCats() {
    this.dataService.searchForCats(this.query).subscribe((response: any) => {
      console.log(response); // Log the response to see if it contains the expected data
      this.cats = response.sentences;
      console.log(this.cats); // Log the cats array after it's been populated
    });
  }   
}

