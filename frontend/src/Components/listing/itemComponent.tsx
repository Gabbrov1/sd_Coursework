import { useEffect, useState } from "react";

export interface Game {
  ID: number;
  Title: string;
  Description: string;
  Categories: string | null;
  Consoles: string | null;
}


export default function GameList() {
  const [games, setGames] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/games")
      .then(res => res.json())
      .then(data => setGames(data));
  }, []);

  return (
    <div>
      {games.map(game => (
        <div  className="game" key={game.ID}>
          <div className="game-top">
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
          
          <div className="game-bottom">
              <p  className="game-description">{game.Description}</p>
          </div>

          
          

        </div>
      ))}
    </div>
  );
}