import React, { useState } from "react";
import {addComment, getComments} from "./asyncFunctions";
import { Code } from "astro:components";

export default function CommentActions({ root,gameID }: { root: string | null ,gameID: number}) {
  const [commentToggle, setCommentToggle] = useState<boolean>(false);
  const [commentText, setCommentText] = useState<string>("");

  function handleCommentSubmit(e: React.FormEvent) {
    e.preventDefault();

    setCommentToggle(false);
    addComment(gameID,root,commentText).then((success) => {
      if (success) {
        getComments(gameID).then((updatedComments) => {
          // Optionally, you can update the comments state here if needed
        });
        setCommentText("");
        return;
      } 

      alert("Failed to submit comment. Please try again.");
    });
  }
  return (
    <>
      <button className="commentInteractButton" onClick={() => setCommentToggle(true)}>Comment</button>
      <button className="commentInteractButton">Like</button>
      <button className="commentInteractButton">Share</button>
      <div className={`commentBox ${commentToggle ? "shown" : "hidden"}`}>
        <form onSubmit={handleCommentSubmit}>
          <input className="textInput" type="text" id="commentBox" placeholder="Write a reply..." value={commentText} onChange={(e) => setCommentText(e.target.value)} />

          <div>
            <button type="submit" className="submitCommentButton" >Submit</button>
            <button type="reset" className="cancelCommentButton" onClick={() => setCommentToggle(false)} >Cancel</button>
          </div>
        </form>
        
      </div>
    </>
  );
}