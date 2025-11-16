import { useEffect, useState } from "react";

export default function GameList() {
  const [games, setGames] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/games")
      .then(res => res.json())
      .then(data => setGames(data));
  }, []);

  return (
    <div>
      <h1>Games</h1>
      {games.map(game => (
        <div key={game.id}>
          <h2>{game.name}</h2>
        </div>
      ))}
    </div>
  );
}