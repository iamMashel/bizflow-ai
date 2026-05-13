import Link from "next/link";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-6 py-12">
      <section className="w-full max-w-md border border-slate-200 bg-white p-8 shadow-sm">
        <Link className="text-sm font-semibold text-slate-600 hover:text-slate-950" href="/">
          BizFlow AI
        </Link>
        <h1 className="mt-8 text-2xl font-semibold tracking-tight text-slate-950">Log in</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          Authentication will be connected to Supabase in a later slice.
        </p>
        <div className="mt-8 rounded-md border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-600">
          Login form placeholder
        </div>
      </section>
    </main>
  );
}
