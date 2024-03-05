import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class MarkovService {
  private apiUrl = 'http://localhost:3000/api/markov';

  constructor(private http: HttpClient) { }

  getMarkovData() {
    return this.http.get(this.apiUrl);
  }
}
