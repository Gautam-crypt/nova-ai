import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const token = request.cookies.get("nova_token")?.value
               || request.headers.get("authorization")?.split(" ")[1]
  
  const { pathname } = request.nextUrl
  
  // Public routes — no auth needed
  const publicRoutes = ["/login", "/register", "/pricing", "/forgot-password", "/"]
  if (publicRoutes.includes(pathname)) return NextResponse.next()
  
  // No token → redirect to login
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url))
  }
  
  // Admin routes — check role from cookie
  if (pathname.startsWith("/admin")) {
    const userJson = request.cookies.get("nova_user")?.value
    if (userJson) {
      try {
        const user = JSON.parse(decodeURIComponent(userJson))
        if (user.role !== "admin") {
          return NextResponse.redirect(new URL("/dashboard", request.url))
        }
      } catch {
        return NextResponse.redirect(new URL("/login", request.url))
      }
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"]
}
