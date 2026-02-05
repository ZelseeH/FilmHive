<p align="center">
  <img src="FilmHiveLogo.png" alt="FilmHive Logo" width="200"/>
</p>
<h1 align="center">FilmHive</h1>
<p align="center">
  System Rekomendacji Filmów oparty na uczeniu maszynowym<br/>
  <i>Praca inżynierska – Informatyka</i>
</p>

FilmHive to aplikacja webowa generująca spersonalizowane rekomendacje filmowe.  
System wykorzystuje hybrydowy algorytm ML (k-NN + Naive Bayes) oparty na podejściu Pazzaniego i Billsusa (content-based filtering).
Aplikacja umożliwia ocenianie filmów, zarządzanie listami, interakcję społecznościową oraz korzystanie z asystenta AI.
​

Przegląd Aplikacji (Sneak Peek)
<div style="display: flex; gap: 20px; flex-wrap: wrap; justify-content: center;"> <img src="main_page.png" alt="Strona główna" style="max-width: 300px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/> <img src="recommendations.png" alt="Rekomendacje" style="max-width: 300px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/> </div> <div style="display: flex; gap: 20px; flex-wrap: wrap; justify-content: center;"> <img src="profile.png" alt="Profil użytkownika" style="max-width: 300px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/> <img src="movies.png" alt="Lista filmów" style="max-width: 300px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/> </div>
Aplikacja oferuje ocenianie filmów, listy osobiste, komentarze, asystenta AI (Gemini) oraz panele admin/moderator. Intuicyjny interfejs React zapewnia płynne doświadczenie na wszystkich urządzeniach.
​

##  Funkcjonalności

-  Rekomendacje Top 20 z dynamicznym score dopasowania  
-  Asystent filmowy AI (Gemini)  
-  Oceny 1–10, komentarze, listy „Ulubione” / „Do obejrzenia”  
-  Panel moderatora (zarządzanie filmami, aktorami, gatunkami)  
-  Zaawansowane filtrowanie + integracja trailerów 


| Warstwa        | Technologie |
|---------------|------------|
| **Backend**   | Python, Flask, SQLAlchemy, Alembic, scikit-learn, JWT |
| **Frontend**  | React + TypeScript, Bootstrap 5, React Router |
| **Baza danych** | PostgreSQL (20+ tabel, relacje many-to-many) |
| **AI/ML**     | TF-IDF, k-NN (cosine similarity), Naive Bayes |
| **Inne**      | Google Gemini, NLTK |
​

Algorytm Rekomendacyjny
Hybrydowy system content-based:

- Profil użytkownika budowany na podstawie ocen i cech filmów  
- k-NN (cosine similarity, k=15)  
- Naive Bayes (Multinomial/Bernoulli)  
- Fuzja wyników: 65% k-NN + 35% NB  
- MMR – zwiększenie różnorodności rekomendacji  

Jakub Kołodziej  
Praca inżynierska – Uniwersytet Bielsko-Bialski  
Kierunek: Informatyka​
