import axios from "axios";

export interface RecentRatedMovie {
    movie_id: number;
    title: string;
    poster_url: string | null;
    rating: number;
    rated_at: string;
}

export async function fetchRecentRatedMovies(username: string): Promise<RecentRatedMovie[]> {
    const response = await axios.get<RecentRatedMovie[]>(`/api/user/profile/${username}/recent-ratings`);
    return response.data;
}
// Dodaj do istniejącego pliku userMoviesService.ts

export async function fetchAllRatedMovies(username: string): Promise<RecentRatedMovie[]> {
    const response = await axios.get<RecentRatedMovie[]>(`/api/user/profile/${username}/all-ratings`);
    return response.data;
}
