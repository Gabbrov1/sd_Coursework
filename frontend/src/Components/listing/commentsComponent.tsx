import { useState, useEffect, useMemo } from "react";
import type { Comment, User } from "./commentHelpers/customTypes";

import CommentActions from "./commentHelpers/commentFunctions";
import { getComments, getUsers } from "./commentHelpers/asyncFunctions";

// Helper functions


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


function CommentContent({ comment, users, gameID }: { comment: Comment; users: Record<string, User>; gameID: number }){
  
  return (
    <>
      <p className="userTag" style={{ background: users[comment.userID.toString()]?.customBackground ?? '' }}>
        <span className="userAvatar" style={{background: `url(${users[comment.userID.toString()]?.avatarImage ?? ''})`,}}/>
        <strong key={comment.userID.toString()}>
          {users[comment.userID.toString()]?.userName ?? 'Unknown User'}
        </strong>
        <span className="timeStamp">{getTimestamp(comment.createdAt)}</span>
      </p>
      <p>{comment.commentText}</p>
      <CommentActions root={comment.parentID} gameID={gameID} />
    </>
  );
}

// ---------- Recursive replies ----------

function renderReplies(replies: Comment[], users: Record<string, User>,gameID:number): any | null {
  if (!replies || replies.length === 0) {
    return null;
  }

  return (
    <div className="repliesHolder">
      {replies.map((reply) => (
        <div key={reply._id} className="reply">
          <div className="comment">
            <CommentContent comment={reply} users={users} gameID={gameID}/>
            {renderReplies(reply.children ?? [], users,gameID)}
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

        setComments(fetchedComments);
        setUsers(fetchedUsers);
      } catch (err) {
        if (cancelled) return;
        console.error("Error loading comments/users:", err);
        setError("Failed to load comments");
      }
    };

    load();

    // Cleanup in case component unmounts mid-request (AI suggestion)
    return () => {
      cancelled = true;
    };
  }, [props.gameID]);
  
  // Memoized user lookup map
  //Changed from find to useMemo for performance(AI suggestion)
  const userMap: Record<string, User> = useMemo(
  () => Object.fromEntries(users.map(u => [u._id, u])),
  [users]
  );

  return (
    <div className="comments-section">
      <h2>Comments Section</h2>

      {error && <p>{error}</p>}

      <div className="commentsHolder">
        {
          comments.length === 0 && !error ? 
          (
            <p>No comments yet. Be the first to comment!</p>
          ) : 
          (
            comments.map((comment) => 
              (
                <div key={comment._id} className="comment">
                  <CommentContent comment={comment} users={userMap} gameID={props.gameID} />
                  {renderReplies(comment.children ?? [], userMap,props.gameID)}
                </div>
              ))
          )
        }
      </div>
    </div>
  );
}
