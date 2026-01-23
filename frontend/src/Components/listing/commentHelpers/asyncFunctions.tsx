import type { Comment, User } from "./customTypes";

export async function addComment(gameID: number, parentID: string | null,commentText: string): Promise<boolean> {
  const res = await fetch(
    `http://localhost:5000/api/games/${gameID}/comments`,
    { 
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: "include",
      body: JSON.stringify({
            "gameID": gameID,
            "parentCommentID": parentID,
            "commentText": commentText,
            "createdAt": new Date().toISOString()
        })
    }
  );
  return res.ok;
}

export async function getComments(gameID: number): Promise<Comment[]> {
  const res = await fetch(
    `http://localhost:5000/api/games/${gameID}/comments`,
    { 
      method: "GET",
      credentials: "include"
    }
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch comments: ${res.status}`);
  }

  const data: { comments: Comment[] } = await res.json();
  return data.comments;
}

export async function getUsers(): Promise<User[]> {
  const res = await fetch(
    `http://localhost:5000/api/users`,
    { 
      method: "GET",
      credentials: "include"
  }
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch user: ${res.status}`);
  }
  const data: getUsersResponse = await res.json();
  return data.users;
}