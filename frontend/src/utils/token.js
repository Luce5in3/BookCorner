// Token 存取工具
const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function setAccessToken(token) {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setRefreshToken(token) {
  localStorage.setItem(REFRESH_TOKEN_KEY, token)
}

export function setTokens(access, refresh) {
  setAccessToken(access)
  setRefreshToken(refresh)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

export function hasToken() {
  return !!getAccessToken()
}
