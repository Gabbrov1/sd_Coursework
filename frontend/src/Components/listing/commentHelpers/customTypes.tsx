export interface Comment {
  _id: string;
  gameID: number;
  parentID: string | null;

  createdAt: string;
  userID: string;
  commentText: string;
  children?: Comment[];
}
export interface User {
  userID: string;
  userName: string;
  avatarImage: string;
  quote: string;
  customBackground: string;
}

export type GetUsersResponse = {
  users: User[];
}