const ERROR_TOASTS: Record<string, string> = {
  NOT_ENOUGH_NERVE: "Not enough nerve!",
  NOT_ENOUGH_ENERGY: "Not enough energy!",
  INCAPACITATED: "You're in jail or hospital!",
  NOT_ENOUGH_CASH: "Not enough cash!",
  INVALID_CREDENTIALS: "Wrong username or password.",
  USERNAME_TAKEN: "Username already taken.",
  SELF_BUST: "Can't bust yourself!",
  SELF_ATTACK: "Can't attack yourself!",
  NOT_FOUND: "Not found.",
  NOT_JAILED: "They're not in jail.",
  NOT_ENOUGH_ITEMS: "Not enough items.",
  DAILY_CAP: "Daily use limit reached.",
  INVALID_LISTING: "Invalid listing parameters.",
  CONCURRENT_BUY: "Someone else bought it first!",
  INVALID_STAT: "Invalid stat.",
}

export function toastMessage(err: any): string {
  const code = err?.message || ''
  return ERROR_TOASTS[code] || code || 'Something went wrong.'
}
