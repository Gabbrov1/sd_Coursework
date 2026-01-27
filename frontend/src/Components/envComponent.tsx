export default function getEnvironment(): string {
  const apiUrl = import.meta.env.API_ROOT;
  return apiUrl;
}