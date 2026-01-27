import { number } from "astro:schema";
import { useEffect, useState } from "react";
import ImageCarousel from "./imageCarousel";
import getEnvironment from '../envComponent';

const apiUrl = getEnvironment();

export interface Game {
  ID: number;
  Title: string;
  Description: string;
  Categories: string | null;
  Consoles: string | null;
  Images: string[];
}

export interface responseData {
  total_pages: number;
  data: Game[];
}


export default function GameList() {
  const [games, setGames] = useState<Game[]>([]);
  const [pageNumber, SetPageNumber] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  function loadGames(page: number, rows: number) {
    return fetch(`${apiUrl}/api/games?pageNr=${page}&rows=${rows}`)
      .then(res => res.json());
  }

  useEffect(() => {
    loadGames(pageNumber, 2)
      .then((data: responseData) => {
        setGames(data.data);
        setTotalPages(data.total_pages);
      })
      .catch(err => console.error("Error:", err));
  }, [pageNumber]);

  return (
    <div className="gamesHolder">
      {games.map(game => (
        <div  className="game" key={game.ID}>
          <div className="game-top">
            <div className="top-left">
              <h2 className="game-title">{game.Title}</h2>
              <ul className="game-categories-holder">
                {game.Categories?.split(",").map(cat => cat.trim()).map((cat, idx) => (
                  <li key={idx} className="game-category">
                    {cat}
                  </li>
                ))}
              </ul>
              <ul className="game-consoles-holder">
                {game.Consoles?.split(",").map(con => con.trim()).map((con, idx) => (
                  <li key={idx} className="game-consoles">
                    {con}
                  </li>
                ))}
              </ul>
            </div>
            <div className="top-right">
                <ImageCarousel images={game.Images}/>
            </div>
          </div>
          
          <div className="game-bottom">
              <p  className="game-description">{game.Description}</p>
          </div>
          <a href={`/games/${game.ID}`}>Open project</a>

        </div>
      ))}
      <div className="pagination">
        
        <button onClick={() => SetPageNumber(pageNumber-1)}>
          Prev
        </button>
        {Array.from({ length: totalPages }, (_, i) => i + 1).map(num => (
          <a key={num} onClick={() => SetPageNumber(num-1)} className={num-1 === pageNumber ? "active" : ""}>
            {num}
          </a>
        ))}
        <button onClick={() => SetPageNumber(pageNumber+1)}>
          Next
        </button>
      </div>
    </div>
  );
}