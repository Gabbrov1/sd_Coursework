import { useState, useEffect } from "react";

export interface Comment {
  commentID: number;
  gameID: number;
  parentID: number | null;

  createdAt: string;
  userName: string;
  commentText: string;
  children?: Comment[];
}
export interface User {
  userID: number;
  userName: string;
  avatarImage: string;
  quote: string;
  customBackground: string;
}

type getUsersResponse = {
  users: User[];
}

async function getComments(gameID: number): Promise<Comment[]> {
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
async function getUsers(): Promise<User[]> {
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
function formatUnit(value: number, unit: string): string {
  const suffix = value === 1 ? "" : "s";
  return `${value} ${unit}${suffix} ago`;
}
function getTimestamp(date: string): string {
  const now = new Date();
  const commentDate = new Date(date);

  if (isNaN(commentDate.getTime())) {
    return "Invalid date";
  }

  const diffInMs = now.getTime() - commentDate.getTime();
  const diffInSeconds = Math.floor(diffInMs / 1000);

  if (diffInSeconds < 60) return "Just now";

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return formatUnit(diffInMinutes, "minute");

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return formatUnit(diffInHours, "hour");

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return formatUnit(diffInDays, "day");

  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks < 4) return formatUnit(diffInWeeks, "week");

  const diffInMonths = Math.floor(diffInDays / 30); // approx
  if (diffInMonths < 12) return formatUnit(diffInMonths, "month");

  const diffInYears = Math.floor(diffInDays / 365);
  return formatUnit(diffInYears, "year");
}


function CommentActions() {
  return (
    <>
      <button className="commentInteractButton">Comment</button>
      <button className="commentInteractButton">Like</button>
      <button className="commentInteractButton">Share</button>
      <div className='commentBox ${commentToggle ? "shown" : "hidden"}'>
        <textarea placeholder="Write a reply..." />
        <div>
          <button className="submitCommentButton">Submit</button>
          <button className="cancelCommentButton" >Cancel</button>
        </div>
      </div>
    </>
  );
}

function CommentContent({ comment, users }: { comment: Comment; users: User[] }){
  const user: User | any = users.find(u => u.userName == comment.userName) ?? {};

  return (
    <>
      <p className="userTag" style={{background: user.customBackground? user.customBackground : ''}}>
        <span className="userAvatar" style={{background: `url(${user.avatarImage? user.avatarImage:''})`}}/>
        <strong>{comment.userName}</strong>
        <span className="timeStamp">{getTimestamp(comment.createdAt)}</span>
      </p>
      <p>{comment.commentText}</p>
      <CommentActions />
    </>
  );
}

// ---------- Recursive replies ----------

function renderReplies(replies: Comment[], users:User[]): any | null {
  if (!replies || replies.length === 0) {
    return null;
  }

  return (
    <div className="repliesHolder">
      {replies.map((reply) => (
        <div key={reply.commentID} className="reply">
          <div className="comment">
            <CommentContent comment={reply} users={users}/>
            {renderReplies(reply.children ?? [], users)}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function CommentsComponent(props: { gameID: number }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [commentToggle, setCommentToggle] = useState<boolean>(false);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setError(null);

        // Fetch comments + users in parallel
        const [fetchedComments, fetchedUsers] = await Promise.all([
          getComments(props.gameID),
          getUsers(),
        ]);

        if (cancelled) return;

        console.log("Fetched comments:", fetchedComments);
        console.log("Fetched users:", fetchedUsers);

        setComments(fetchedComments);
        setUsers(fetchedUsers);
      } catch (err) {
        if (cancelled) return;
        console.error("Error loading comments/users:", err);
        setError("Failed to load comments");
      }
    };

    load();

    // Cleanup in case component unmounts mid-request
    return () => {
      cancelled = true;
    };
  }, [props.gameID]);


  return (
    <div>
      <h2>Comments Section</h2>

      {error && <p>{error}</p>}

      <div className="commentsHolder">
        {comments.length === 0 && !error && <p>No comments yet.</p>}

        {comments.map((comment) => (
          <div key={comment.commentID} className="comment">
            <CommentContent comment={comment} users={users} />
            {renderReplies(comment.children ?? [],users)}
          </div>
        ))}
      </div>
    </div>
  );
}
