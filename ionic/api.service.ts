import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

interface SearchResult {
  sentences?: string[];
  text?: string;
  citations?: {[key: string]: number}[];
  top_citations?: {[key: string]: number}[];
}


@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'https://amock.io/api/Trogluddite';

  constructor(private http: HttpClient) { }

 search(query: string, clean: boolean = false, showSources: boolean = false): Observable<SearchResult> {
    let url;
    if (query.toLowerCase() === 'cats' && showSources) {
      // Directly using the specified URL for "cats" with showSources
      url = 'https://amock.io/api/Trogluddite/search?q=cats&show_sources=true';
    } else {
      // General case for other queries
      const endpoint = clean ? 'search_clean' : 'search';
      url = `${this.baseUrl}/${endpoint}?q=${query}${showSources ? '&show_sources=true' : ''}`;
    }
  
    return this.http.get<SearchResult>(url).pipe(
      map(data => {
        console.log("Data received from API:", data);  // Log the data to debug
        return data as SearchResult;  // Assume data is always in the correct format
      }),
      catchError(error => {
        console.error('Error fetching data: ', error);
        return of({}); // Return an Observable with an empty SearchResult
      })
    );
  }
}  
