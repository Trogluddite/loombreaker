import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'https://amock.io/api/Trogluddite';

  constructor(private http: HttpClient) { }

  search(query: string): Observable<any> {
    const url = `${this.baseUrl}/search?q=${query}&show_sources=true`;
    return this.http.get(url);
  }
}
