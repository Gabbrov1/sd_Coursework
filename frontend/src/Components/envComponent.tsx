export default function getEnvironment(): string {
  const apiUrl = import.meta.env.PUBLIC_API_ROOT;
  return apiUrl;
}