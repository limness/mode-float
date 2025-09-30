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
      return Math.min(next, target - 5)
    }

    if (phase === 'mid') {
      simulated += randomBetween(2, 4)
      const eased = easeInOut(Math.min(simulated / 100, 1)) * (target - 10)
      if (eased >= target - 12) {
        phase = 'end'
      }
      return Math.min(prev + (eased - prev) * 0.4 + noise, target - 5)
    }

    const finalKick = prev + randomBetween(6, 12)
    return Math.min(finalKick, target)
  }
}
