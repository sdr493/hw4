export default function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="error" role="alert">
      <strong>Something went wrong.</strong> {message}. Make sure the backend is running and try again.
    </div>
  )
}
