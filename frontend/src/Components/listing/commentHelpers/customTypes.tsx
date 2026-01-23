export interface Comment {
  _id: string;
  gameID: number;
  parentID: string | null;

  createdAt: string;
  userName: string;
  userID: number;
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