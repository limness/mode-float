export type ProgressPattern = (prev: number) => number

function randomBetween(min: number, max: number) {
  return Math.random() * (max - min) + min
}

function easeInOut(t: number) {
  return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1
}

export function createProgressPattern(target: number) {
  let phase = 'start'
  let simulated = 0
  const maxBeforeTarget = Math.max(target - randomBetween(8, 15), 10)

  const toIntegerProgress = (value: number, prev: number) => {
    const clamped = Math.min(value, target)
    const rounded = Math.round(clamped)
    if (rounded <= prev) {
      return Math.min(target, prev + 1)
    }
    return rounded
  }

  return (prev: number) => {
    if (prev >= target) {
      return target
    }

    const noise = randomBetween(0, 3)

    if (phase === 'start') {
      simulated += randomBetween(3, 8)
      const next = Math.min(simulated + noise, maxBeforeTarget)
      if (next >= maxBeforeTarget) {
        phase = 'mid'
      }
      return toIntegerProgress(Math.min(next, target - 5), prev)
    }

    if (phase === 'mid') {
      simulated += randomBetween(2, 4)
      const eased = easeInOut(Math.min(simulated / 100, 1)) * (target - 10)
      if (eased >= target - 12) {
        phase = 'end'
      }
      const midProgress = prev + (eased - prev) * 0.4 + noise
      return toIntegerProgress(Math.min(midProgress, target - 5), prev)
    }

    const finalKick = prev + randomBetween(6, 12)
    return toIntegerProgress(finalKick, prev)
  }
}
