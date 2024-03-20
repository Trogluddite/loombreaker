import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class DataService {

    constructor(private http: HttpClient) { }

    searchForCats(query: string): Observable<any> {
        return this.http.get(`https://amock.io/api/Trogluddite/search?q=${query}`);
      }
      
    
}
