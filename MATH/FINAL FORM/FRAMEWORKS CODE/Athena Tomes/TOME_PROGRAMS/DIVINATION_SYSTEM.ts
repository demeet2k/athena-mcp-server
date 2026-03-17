/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * DIVINATION SYSTEM - Complete Multi-Calendar Integration
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Integration of multiple calendar and divinatory systems:
 * 
 * Mayan: 18980-day Calendar Round + 37960-day Double Round
 *   - Tzolkin (260-day sacred calendar)
 *   - Haab (365-day civil calendar)
 *   - Long Count (baktun.katun.tun.uinal.kin)
 * 
 * Vedic: Yuga cycles with 4:3:2:1 ratio
 *   - Satya Yuga: 1,728,000 years
 *   - Treta Yuga: 1,296,000 years
 *   - Dwapara Yuga: 864,000 years
 *   - Kali Yuga: 432,000 years
 * 
 * Hebrew/Torah: Divine name permutations
 *   - 12 YHVH permutations for months
 *   - 42-letter divine name (Ana BeKoach)
 *   - 72-letter divine name
 * 
 * Position tracking: Position = (n, Θ, X, Δ, Cert)
 * 
 * @module DIVINATION_SYSTEM
 * @version 2.0.0
 */

import { TruthValue, WitnessPtr } from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: GREGORIAN/JULIAN DAY CALCULATIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Convert Gregorian date to Julian Day Number
 * Algorithm from Astronomical Algorithms by Jean Meeus
 */
export function gregorianToJD(year: number, month: number, day: number): number {
  if (month <= 2) {
    year -= 1;
    month += 12;
  }
  
  const A = Math.floor(year / 100);
  const B = 2 - A + Math.floor(A / 4);
  
  return Math.floor(365.25 * (year + 4716)) +
         Math.floor(30.6001 * (month + 1)) +
         day + B - 1524.5;
}

/**
 * Convert Julian Day Number to Gregorian date
 */
export function jdToGregorian(jd: number): { year: number; month: number; day: number } {
  const Z = Math.floor(jd + 0.5);
  const F = (jd + 0.5) - Z;
  
  let A: number;
  if (Z < 2299161) {
    A = Z;
  } else {
    const alpha = Math.floor((Z - 1867216.25) / 36524.25);
    A = Z + 1 + alpha - Math.floor(alpha / 4);
  }
  
  const B = A + 1524;
  const C = Math.floor((B - 122.1) / 365.25);
  const D = Math.floor(365.25 * C);
  const E = Math.floor((B - D) / 30.6001);
  
  const day = B - D - Math.floor(30.6001 * E) + F;
  const month = E < 14 ? E - 1 : E - 13;
  const year = month > 2 ? C - 4716 : C - 4715;
  
  return { year, month, day: Math.floor(day) };
}

/**
 * Check if year is a leap year
 */
export function isLeapYear(year: number): boolean {
  return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
}

/**
 * Days in month
 */
export function daysInMonth(year: number, month: number): number {
  const days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (month === 2 && isLeapYear(year)) {
    return 29;
  }
  return days[month - 1];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: MAYAN CALENDAR SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/** Mayan calendar constants */
export const MAYAN = {
  /** Tzolkin cycle length */
  TZOLKIN_LENGTH: 260,
  
  /** Haab cycle length */
  HAAB_LENGTH: 365,
  
  /** Calendar Round (LCM of Tzolkin and Haab) */
  CALENDAR_ROUND: 18980,
  
  /** Double Calendar Round */
  DOUBLE_ROUND: 37960,
  
  /** Julian Day of Mayan creation date (13.0.0.0.0 4 Ahau 8 Cumku) */
  CREATION_JD: 584283,  // August 11, 3114 BCE
  
  /** Long Count units */
  KIN: 1,
  UINAL: 20,
  TUN: 360,
  KATUN: 7200,
  BAKTUN: 144000
};

/** Tzolkin day signs (20) */
export const TZOLKIN_SIGNS = [
  "Imix", "Ik", "Akbal", "Kan", "Chicchan",
  "Cimi", "Manik", "Lamat", "Muluc", "Oc",
  "Chuen", "Eb", "Ben", "Ix", "Men",
  "Cib", "Caban", "Etznab", "Cauac", "Ahau"
];

/** Haab months (18 + Wayeb) */
export const HAAB_MONTHS = [
  "Pop", "Uo", "Zip", "Zotz", "Tzec",
  "Xul", "Yaxkin", "Mol", "Chen", "Yax",
  "Zac", "Ceh", "Mac", "Kankin", "Muan",
  "Pax", "Kayab", "Cumku", "Wayeb"
];

export interface MayanDate {
  /** Long Count */
  longCount: {
    baktun: number;
    katun: number;
    tun: number;
    uinal: number;
    kin: number;
  };
  
  /** Tzolkin (Sacred Calendar) */
  tzolkin: {
    number: number;  // 1-13
    sign: number;    // 0-19 (index into TZOLKIN_SIGNS)
    signName: string;
  };
  
  /** Haab (Civil Calendar) */
  haab: {
    day: number;     // 0-19 (or 0-4 for Wayeb)
    month: number;   // 0-18 (index into HAAB_MONTHS)
    monthName: string;
  };
  
  /** Days since creation */
  dayCount: number;
  
  /** Position in Calendar Round (0 to 18979) */
  calendarRoundPosition: number;
}

/**
 * Convert Julian Day to Mayan date
 */
export function jdToMayan(jd: number): MayanDate {
  const dayCount = Math.floor(jd) - MAYAN.CREATION_JD;
  
  // Long Count
  let remaining = dayCount;
  const baktun = Math.floor(remaining / MAYAN.BAKTUN);
  remaining %= MAYAN.BAKTUN;
  const katun = Math.floor(remaining / MAYAN.KATUN);
  remaining %= MAYAN.KATUN;
  const tun = Math.floor(remaining / MAYAN.TUN);
  remaining %= MAYAN.TUN;
  const uinal = Math.floor(remaining / MAYAN.UINAL);
  const kin = remaining % MAYAN.UINAL;
  
  // Tzolkin
  // At creation: 4 Ahau
  const tzolkinNumber = ((dayCount + 3) % 13) + 1;  // +3 because creation was 4
  const tzolkinSign = (dayCount + 19) % 20;  // +19 because creation was Ahau (19)
  
  // Haab
  // At creation: 8 Cumku
  const haabDayOfYear = (dayCount + 348) % MAYAN.HAAB_LENGTH;  // 8 Cumku = day 348
  const haabMonth = Math.floor(haabDayOfYear / 20);
  const haabDay = haabDayOfYear % 20;
  
  // Calendar Round position
  const calendarRoundPosition = ((dayCount % MAYAN.CALENDAR_ROUND) + MAYAN.CALENDAR_ROUND) % MAYAN.CALENDAR_ROUND;
  
  return {
    longCount: { baktun, katun, tun, uinal, kin },
    tzolkin: {
      number: tzolkinNumber,
      sign: tzolkinSign,
      signName: TZOLKIN_SIGNS[tzolkinSign]
    },
    haab: {
      day: haabDay,
      month: haabMonth,
      monthName: HAAB_MONTHS[haabMonth]
    },
    dayCount,
    calendarRoundPosition
  };
}

/**
 * Convert Mayan Long Count to Julian Day
 */
export function mayanToJD(baktun: number, katun: number, tun: number, uinal: number, kin: number): number {
  const dayCount = baktun * MAYAN.BAKTUN +
                   katun * MAYAN.KATUN +
                   tun * MAYAN.TUN +
                   uinal * MAYAN.UINAL +
                   kin;
  return dayCount + MAYAN.CREATION_JD;
}

/**
 * Format Long Count
 */
export function formatLongCount(lc: MayanDate["longCount"]): string {
  return `${lc.baktun}.${lc.katun}.${lc.tun}.${lc.uinal}.${lc.kin}`;
}

/**
 * Format Tzolkin
 */
export function formatTzolkin(tz: MayanDate["tzolkin"]): string {
  return `${tz.number} ${tz.signName}`;
}

/**
 * Format Haab
 */
export function formatHaab(hb: MayanDate["haab"]): string {
  return `${hb.day} ${hb.monthName}`;
}

/**
 * Get next Calendar Round alignment
 */
export function nextCalendarRound(jd: number): number {
  const mayan = jdToMayan(jd);
  const remaining = MAYAN.CALENDAR_ROUND - mayan.calendarRoundPosition;
  return jd + remaining;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: VEDIC/HINDU CALENDAR SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/** Vedic calendar constants */
export const VEDIC = {
  /** Yuga lengths in years */
  SATYA_YUGA: 1728000,
  TRETA_YUGA: 1296000,
  DWAPARA_YUGA: 864000,
  KALI_YUGA: 432000,
  
  /** Maha Yuga (complete cycle) */
  MAHA_YUGA: 4320000,
  
  /** Manvantara (71 Maha Yugas + Sandhya) */
  MANVANTARA: 306720000,
  
  /** Kalpa (14 Manvantaras) */
  KALPA: 4320000000,
  
  /** Kali Yuga start (Julian Day) - Feb 18, 3102 BCE */
  KALI_YUGA_START_JD: 588466,
  
  /** Ratio of Yugas */
  YUGA_RATIO: [4, 3, 2, 1],
  
  /** Lunar month in days */
  SYNODIC_MONTH: 29.530589,
  
  /** Tithi (lunar day) */
  TITHI: 29.530589 / 30
};

/** Nakshatra (lunar mansions) */
export const NAKSHATRAS = [
  { name: "Ashwini", deity: "Ashwini Kumaras" },
  { name: "Bharani", deity: "Yama" },
  { name: "Krittika", deity: "Agni" },
  { name: "Rohini", deity: "Brahma" },
  { name: "Mrigashira", deity: "Soma" },
  { name: "Ardra", deity: "Rudra" },
  { name: "Punarvasu", deity: "Aditi" },
  { name: "Pushya", deity: "Brihaspati" },
  { name: "Ashlesha", deity: "Nagas" },
  { name: "Magha", deity: "Pitris" },
  { name: "Purva Phalguni", deity: "Bhaga" },
  { name: "Uttara Phalguni", deity: "Aryaman" },
  { name: "Hasta", deity: "Savitar" },
  { name: "Chitra", deity: "Vishwakarma" },
  { name: "Swati", deity: "Vayu" },
  { name: "Vishakha", deity: "Indra-Agni" },
  { name: "Anuradha", deity: "Mitra" },
  { name: "Jyeshtha", deity: "Indra" },
  { name: "Mula", deity: "Nirrti" },
  { name: "Purva Ashadha", deity: "Apas" },
  { name: "Uttara Ashadha", deity: "Vishvedevas" },
  { name: "Shravana", deity: "Vishnu" },
  { name: "Dhanishtha", deity: "Vasus" },
  { name: "Shatabhisha", deity: "Varuna" },
  { name: "Purva Bhadrapada", deity: "Aja Ekapada" },
  { name: "Uttara Bhadrapada", deity: "Ahir Budhnya" },
  { name: "Revati", deity: "Pushan" }
];

/** Tithi names */
export const TITHIS = [
  "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
  "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
  "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
];

export interface VedicDate {
  /** Current Yuga */
  yuga: "Satya" | "Treta" | "Dwapara" | "Kali";
  
  /** Years into current Yuga */
  yearInYuga: number;
  
  /** Tithi (lunar day) */
  tithi: {
    number: number;      // 1-15
    name: string;
    paksha: "Shukla" | "Krishna";  // Bright/Dark fortnight
  };
  
  /** Nakshatra (lunar mansion) */
  nakshatra: {
    number: number;      // 0-26
    name: string;
    deity: string;
  };
  
  /** Masa (lunar month) */
  masa: number;
  
  /** Samvatsara (60-year cycle) */
  samvatsara: number;
}

/**
 * Convert Julian Day to Vedic date
 */
export function jdToVedic(jd: number): VedicDate {
  const daysFromKaliStart = jd - VEDIC.KALI_YUGA_START_JD;
  const yearsFromKaliStart = daysFromKaliStart / 365.25;
  
  // Current Yuga (we're in Kali Yuga)
  const yuga: VedicDate["yuga"] = "Kali";
  const yearInYuga = Math.floor(yearsFromKaliStart);
  
  // Tithi calculation (simplified - based on lunar phase)
  const lunarCycle = (jd - 2451550.1) / VEDIC.SYNODIC_MONTH;  // Reference: Jan 6, 2000 new moon
  const lunarPhase = (lunarCycle - Math.floor(lunarCycle)) * 30;
  const tithiNumber = (Math.floor(lunarPhase) % 15) + 1;
  const paksha = Math.floor(lunarPhase / 15) === 0 ? "Shukla" : "Krishna";
  
  // Nakshatra calculation (simplified - based on lunar position)
  const nakshatraNumber = Math.floor((lunarPhase / 30) * 27) % 27;
  
  // Masa (lunar month)
  const masa = Math.floor(lunarCycle) % 12;
  
  // Samvatsara (60-year cycle)
  const samvatsara = Math.floor(yearsFromKaliStart) % 60;
  
  return {
    yuga,
    yearInYuga,
    tithi: {
      number: tithiNumber,
      name: TITHIS[tithiNumber - 1],
      paksha
    },
    nakshatra: {
      number: nakshatraNumber,
      name: NAKSHATRAS[nakshatraNumber].name,
      deity: NAKSHATRAS[nakshatraNumber].deity
    },
    masa,
    samvatsara
  };
}

/**
 * Get Yuga position as fraction of Maha Yuga
 */
export function getYugaPosition(jd: number): {
  mahaYugaFraction: number;
  yugaName: string;
  yugaFraction: number;
} {
  const daysFromKaliStart = jd - VEDIC.KALI_YUGA_START_JD;
  const yearsFromKaliStart = daysFromKaliStart / 365.25;
  
  // We're in Kali Yuga (last quarter of Maha Yuga)
  const mahaYugaFraction = (VEDIC.SATYA_YUGA + VEDIC.TRETA_YUGA + VEDIC.DWAPARA_YUGA + yearsFromKaliStart) / VEDIC.MAHA_YUGA;
  const yugaFraction = yearsFromKaliStart / VEDIC.KALI_YUGA;
  
  return {
    mahaYugaFraction,
    yugaName: "Kali",
    yugaFraction
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: HEBREW/KABBALISTIC SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/** Hebrew constants */
export const HEBREW = {
  /** Hebrew epoch (Julian Day of Tishri 1, Year 1) */
  EPOCH_JD: 347995.5,  // September 7, 3761 BCE
  
  /** Molad interval (average lunar month) */
  MOLAD_INTERVAL: 29.530594,
  
  /** Hebrew year types */
  YEAR_DEFICIENT: 353,
  YEAR_REGULAR: 354,
  YEAR_COMPLETE: 355,
  LEAP_DEFICIENT: 383,
  LEAP_REGULAR: 384,
  LEAP_COMPLETE: 385
};

/** 12 permutations of YHVH for months */
export const YHVH_PERMUTATIONS = [
  { month: "Nisan", permutation: "יהוה", meaning: "Will be" },
  { month: "Iyar", permutation: "יההו", meaning: "Healing" },
  { month: "Sivan", permutation: "יוהה", meaning: "Giving" },
  { month: "Tammuz", permutation: "הוהי", meaning: "Intensity" },
  { month: "Av", permutation: "ההוי", meaning: "Vision" },
  { month: "Elul", permutation: "הויה", meaning: "Transformation" },
  { month: "Tishrei", permutation: "והיה", meaning: "Being" },
  { month: "Cheshvan", permutation: "והה", meaning: "Holding" },
  { month: "Kislev", permutation: "ויהה", meaning: "Dreams" },
  { month: "Tevet", permutation: "ההי", meaning: "Testing" },
  { month: "Shevat", permutation: "ההי", meaning: "Renewal" },
  { month: "Adar", permutation: "יההו", meaning: "Joy" }
];

/** 42-Letter Divine Name (Ana BeKoach) - 7 lines of 6 letters */
export const ANA_BEKOACH = [
  { line: 1, letters: "אבגיתץ", attribute: "Chesed" },
  { line: 2, letters: "קרעשטן", attribute: "Gevurah" },
  { line: 3, letters: "נגדיכש", attribute: "Tiferet" },
  { line: 4, letters: "בטרצתג", attribute: "Netzach" },
  { line: 5, letters: "חקבטנע", attribute: "Hod" },
  { line: 6, letters: "יגלפזק", attribute: "Yesod" },
  { line: 7, letters: "שקוצית", attribute: "Malkhut" }
];

/** 72 Divine Names (Shem HaMephorash) */
export const SHEM_72 = [
  "והו", "ילי", "סיט", "עלם", "מהש", "ללה", "אכא", "כהת",
  "הזי", "אלד", "לאו", "ההע", "יזל", "מבה", "הרי", "הקם",
  "לאו", "כלי", "לוו", "פהל", "נלכ", "ייי", "מלה", "חהו",
  "נתה", "האא", "ירת", "שאה", "ריי", "אום", "לכב", "ושר",
  "יחו", "להח", "כוק", "מנד", "אני", "חעם", "רהע", "ייז",
  "ההה", "מיכ", "וול", "ילה", "סאל", "ערי", "עשל", "מיה",
  "והו", "דני", "החש", "עמם", "ננא", "נית", "מבה", "פוי",
  "נמם", "ייל", "הרח", "מצר", "ומב", "יהה", "ענו", "מחי",
  "דמב", "מנק", "איע", "חבו", "ראה", "יבם", "היי", "מום"
];

export interface HebrewDate {
  /** Hebrew year */
  year: number;
  
  /** Hebrew month (1-13) */
  month: number;
  
  /** Month name */
  monthName: string;
  
  /** Day of month (1-30) */
  day: number;
  
  /** Is leap year */
  isLeapYear: boolean;
  
  /** YHVH permutation for month */
  yhvhPermutation: string;
  
  /** Day of week (0=Sunday) */
  dayOfWeek: number;
}

/**
 * Is Hebrew year a leap year
 */
export function isHebrewLeapYear(year: number): boolean {
  return ((7 * year + 1) % 19) < 7;
}

/**
 * Hebrew month names
 */
export function getHebrewMonthName(month: number, isLeapYear: boolean): string {
  const months = [
    "Nisan", "Iyar", "Sivan", "Tammuz", "Av", "Elul",
    "Tishrei", "Cheshvan", "Kislev", "Tevet", "Shevat"
  ];
  
  if (isLeapYear) {
    if (month === 12) return "Adar I";
    if (month === 13) return "Adar II";
  } else {
    if (month === 12) return "Adar";
  }
  
  return months[month - 1] || "Unknown";
}

/**
 * Simplified Hebrew date calculation
 */
export function jdToHebrew(jd: number): HebrewDate {
  // Simplified calculation - for accurate results use a full Hebrew calendar library
  const daysFromEpoch = jd - HEBREW.EPOCH_JD;
  
  // Approximate year
  const approxYear = Math.floor(daysFromEpoch / 365.25) + 1;
  
  // Approximate month (1-12 or 1-13)
  const isLeap = isHebrewLeapYear(approxYear);
  const monthsInYear = isLeap ? 13 : 12;
  const dayOfYear = daysFromEpoch % 365;
  const approxMonth = Math.floor((dayOfYear / 365) * monthsInYear) + 1;
  
  // Day of month
  const day = Math.floor(dayOfYear % 30) + 1;
  
  // Day of week
  const dayOfWeek = Math.floor(jd + 1.5) % 7;
  
  const monthIndex = ((approxMonth - 1) % 12);
  const yhvhPermutation = YHVH_PERMUTATIONS[monthIndex]?.permutation || "";
  
  return {
    year: approxYear,
    month: approxMonth,
    monthName: getHebrewMonthName(approxMonth, isLeap),
    day,
    isLeapYear: isLeap,
    yhvhPermutation,
    dayOfWeek
  };
}

/**
 * Get Ana BeKoach line for day of week
 */
export function getAnaBeKoachLine(dayOfWeek: number): typeof ANA_BEKOACH[0] {
  return ANA_BEKOACH[dayOfWeek % 7];
}

/**
 * Get Shem 72 name for 5-day period
 */
export function getShem72(dayOfYear: number): string {
  const index = Math.floor(dayOfYear / 5) % 72;
  return SHEM_72[index];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: UNIFIED POSITION SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Complete divination position: Position = (n, Θ, X, Δ, Cert)
 * 
 * n: Day number (Julian Day)
 * Θ: Phase vector (all calendar cycles)
 * X: Cross-references between systems
 * Δ: Delta from significant alignments
 * Cert: Certification level
 */
export interface DivinationPosition {
  /** Julian Day number */
  n: number;
  
  /** Gregorian date */
  gregorian: { year: number; month: number; day: number };
  
  /** Phase vector (0 to 2π for each cycle) */
  theta: PhaseVector;
  
  /** All calendar positions */
  calendars: {
    mayan: MayanDate;
    vedic: VedicDate;
    hebrew: HebrewDate;
  };
  
  /** Cross-references */
  crossRefs: CrossReference[];
  
  /** Delta from significant alignments */
  delta: AlignmentDelta[];
  
  /** Certification */
  cert: {
    truth: TruthValue;
    witnessPtr?: string;
    confidence: number;
  };
}

export interface PhaseVector {
  /** Week phase (0 to 2π over 7 days) */
  week: number;
  
  /** Tzolkin phase (0 to 2π over 260 days) */
  tzolkin: number;
  
  /** Haab phase (0 to 2π over 365 days) */
  haab: number;
  
  /** Calendar Round phase (0 to 2π over 18980 days) */
  calendarRound: number;
  
  /** Synodic month phase (0 to 2π over 29.53 days) */
  synodicMonth: number;
  
  /** Solar year phase (0 to 2π over 365.25 days) */
  solarYear: number;
  
  /** Samvatsara phase (0 to 2π over 60 years) */
  samvatsara: number;
}

export interface CrossReference {
  system1: string;
  system2: string;
  relation: string;
  significance: number;
}

export interface AlignmentDelta {
  name: string;
  daysUntil: number;
  significance: "major" | "minor" | "rare";
}

/**
 * Compute complete divination position
 */
export function computePosition(jd: number): DivinationPosition {
  const gregorian = jdToGregorian(jd);
  const mayan = jdToMayan(jd);
  const vedic = jdToVedic(jd);
  const hebrew = jdToHebrew(jd);
  
  // Compute phase vector
  const theta = computePhaseVector(jd);
  
  // Find cross-references
  const crossRefs = findCrossReferences(mayan, vedic, hebrew);
  
  // Compute deltas to significant alignments
  const delta = computeAlignmentDeltas(jd, mayan);
  
  return {
    n: jd,
    gregorian,
    theta,
    calendars: { mayan, vedic, hebrew },
    crossRefs,
    delta,
    cert: {
      truth: TruthValue.NEAR,
      confidence: 0.9
    }
  };
}

/**
 * Compute phase vector for all cycles
 */
export function computePhaseVector(jd: number): PhaseVector {
  const TWO_PI = 2 * Math.PI;
  
  return {
    week: ((jd + 0.5) % 7) / 7 * TWO_PI,
    tzolkin: (jd % MAYAN.TZOLKIN_LENGTH) / MAYAN.TZOLKIN_LENGTH * TWO_PI,
    haab: (jd % MAYAN.HAAB_LENGTH) / MAYAN.HAAB_LENGTH * TWO_PI,
    calendarRound: (jd % MAYAN.CALENDAR_ROUND) / MAYAN.CALENDAR_ROUND * TWO_PI,
    synodicMonth: ((jd - 2451550.1) % VEDIC.SYNODIC_MONTH) / VEDIC.SYNODIC_MONTH * TWO_PI,
    solarYear: (jd % 365.25) / 365.25 * TWO_PI,
    samvatsara: ((jd - VEDIC.KALI_YUGA_START_JD) % (60 * 365.25)) / (60 * 365.25) * TWO_PI
  };
}

function findCrossReferences(
  mayan: MayanDate,
  vedic: VedicDate,
  hebrew: HebrewDate
): CrossReference[] {
  const refs: CrossReference[] = [];
  
  // Example: Tzolkin sign aligned with Nakshatra
  if (mayan.tzolkin.sign === vedic.nakshatra.number % 20) {
    refs.push({
      system1: "Mayan.Tzolkin",
      system2: "Vedic.Nakshatra",
      relation: "Sign alignment",
      significance: 0.7
    });
  }
  
  // Example: Hebrew day of week matches Mayan kin
  if (hebrew.dayOfWeek === mayan.longCount.kin % 7) {
    refs.push({
      system1: "Hebrew.DayOfWeek",
      system2: "Mayan.Kin",
      relation: "Day alignment",
      significance: 0.5
    });
  }
  
  return refs;
}

function computeAlignmentDeltas(jd: number, mayan: MayanDate): AlignmentDelta[] {
  const deltas: AlignmentDelta[] = [];
  
  // Next Calendar Round
  const nextCR = MAYAN.CALENDAR_ROUND - mayan.calendarRoundPosition;
  deltas.push({
    name: "Calendar Round",
    daysUntil: nextCR,
    significance: nextCR < 365 ? "major" : "minor"
  });
  
  // Next Tzolkin cycle
  const nextTzolkin = MAYAN.TZOLKIN_LENGTH - (mayan.dayCount % MAYAN.TZOLKIN_LENGTH);
  deltas.push({
    name: "Tzolkin Cycle",
    daysUntil: nextTzolkin,
    significance: "minor"
  });
  
  // Next Haab cycle
  const nextHaab = MAYAN.HAAB_LENGTH - (mayan.dayCount % MAYAN.HAAB_LENGTH);
  deltas.push({
    name: "Haab Cycle",
    daysUntil: nextHaab,
    significance: "minor"
  });
  
  return deltas;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: DIVINATION ORACLE
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Divination Oracle: unified query interface
 */
export class DivinationOracle {
  /**
   * Query for a specific date
   */
  query(year: number, month: number, day: number): DivinationPosition {
    const jd = gregorianToJD(year, month, day);
    return computePosition(jd);
  }
  
  /**
   * Query for today
   */
  today(): DivinationPosition {
    const now = new Date();
    return this.query(now.getFullYear(), now.getMonth() + 1, now.getDate());
  }
  
  /**
   * Find next significant alignment
   */
  findNextAlignment(
    jd: number,
    maxDays: number = 365
  ): { jd: number; alignment: string; position: DivinationPosition } | null {
    for (let d = 1; d <= maxDays; d++) {
      const pos = computePosition(jd + d);
      
      // Check for significant alignments
      if (pos.crossRefs.some(r => r.significance > 0.8)) {
        return {
          jd: jd + d,
          alignment: pos.crossRefs.filter(r => r.significance > 0.8).map(r => r.relation).join(", "),
          position: pos
        };
      }
      
      // Check for round numbers in Mayan calendar
      const lc = pos.calendars.mayan.longCount;
      if (lc.kin === 0 && lc.uinal === 0) {
        return {
          jd: jd + d,
          alignment: `Long Count ${formatLongCount(lc)}`,
          position: pos
        };
      }
    }
    
    return null;
  }
  
  /**
   * Get readings for a position
   */
  getReadings(pos: DivinationPosition): DivinationReading {
    const mayan = pos.calendars.mayan;
    const vedic = pos.calendars.vedic;
    const hebrew = pos.calendars.hebrew;
    
    return {
      date: `${pos.gregorian.year}-${pos.gregorian.month.toString().padStart(2, '0')}-${pos.gregorian.day.toString().padStart(2, '0')}`,
      
      mayan: {
        longCount: formatLongCount(mayan.longCount),
        tzolkin: formatTzolkin(mayan.tzolkin),
        haab: formatHaab(mayan.haab),
        interpretation: `Day sign ${mayan.tzolkin.signName} represents the energy of ${TZOLKIN_INTERPRETATIONS[mayan.tzolkin.sign]}`
      },
      
      vedic: {
        tithi: `${vedic.tithi.paksha} ${vedic.tithi.name}`,
        nakshatra: `${vedic.nakshatra.name} (ruled by ${vedic.nakshatra.deity})`,
        interpretation: `Nakshatra ${vedic.nakshatra.name} is favorable for ${NAKSHATRA_ACTIVITIES[vedic.nakshatra.number % 5]}`
      },
      
      hebrew: {
        date: `${hebrew.day} ${hebrew.monthName} ${hebrew.year}`,
        yhvh: hebrew.yhvhPermutation,
        anaBeKoach: getAnaBeKoachLine(hebrew.dayOfWeek),
        interpretation: `The divine energy of ${hebrew.monthName} supports ${YHVH_PERMUTATIONS.find(p => p.month === hebrew.monthName)?.meaning || 'growth'}`
      },
      
      synthesis: generateSynthesis(pos)
    };
  }
}

export interface DivinationReading {
  date: string;
  mayan: {
    longCount: string;
    tzolkin: string;
    haab: string;
    interpretation: string;
  };
  vedic: {
    tithi: string;
    nakshatra: string;
    interpretation: string;
  };
  hebrew: {
    date: string;
    yhvh: string;
    anaBeKoach: typeof ANA_BEKOACH[0];
    interpretation: string;
  };
  synthesis: string;
}

const TZOLKIN_INTERPRETATIONS = [
  "primordial waters, inception",
  "breath, spirit, communication",
  "darkness, introspection, mystery",
  "seed, potential, network",
  "serpent, life force, instinct",
  "transformation, death, release",
  "deer, gentleness, tools",
  "star, harmony, art",
  "water, emotions, purification",
  "dog, loyalty, guidance",
  "monkey, play, creativity",
  "road, journey, human condition",
  "reed, authority, alignment",
  "jaguar, magic, night",
  "eagle, vision, freedom",
  "vulture, wisdom, karma",
  "earth, movement, synchronicity",
  "flint, truth, self-reflection",
  "storm, catalyzation, energy",
  "sun, enlightenment, wholeness"
];

const NAKSHATRA_ACTIVITIES = [
  "new beginnings and initiatives",
  "healing and restoration",
  "learning and study",
  "creative endeavors",
  "spiritual practices"
];

function generateSynthesis(pos: DivinationPosition): string {
  const mayan = pos.calendars.mayan;
  const vedic = pos.calendars.vedic;
  const hebrew = pos.calendars.hebrew;
  
  const parts = [
    `The energies of ${mayan.tzolkin.signName} (Mayan) combine with`,
    `${vedic.nakshatra.name} (Vedic) and the ${hebrew.monthName} frequencies (Hebrew).`,
  ];
  
  if (pos.crossRefs.length > 0) {
    parts.push(`Notable alignments: ${pos.crossRefs.map(r => r.relation).join(", ")}.`);
  }
  
  if (pos.delta.some(d => d.daysUntil < 30 && d.significance !== "minor")) {
    const upcoming = pos.delta.find(d => d.daysUntil < 30 && d.significance !== "minor");
    if (upcoming) {
      parts.push(`${upcoming.name} approaches in ${upcoming.daysUntil} days.`);
    }
  }
  
  return parts.join(" ");
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  // Gregorian
  gregorianToJD,
  jdToGregorian,
  isLeapYear,
  daysInMonth,
  
  // Mayan
  MAYAN,
  TZOLKIN_SIGNS,
  HAAB_MONTHS,
  jdToMayan,
  mayanToJD,
  formatLongCount,
  formatTzolkin,
  formatHaab,
  nextCalendarRound,
  
  // Vedic
  VEDIC,
  NAKSHATRAS,
  TITHIS,
  jdToVedic,
  getYugaPosition,
  
  // Hebrew
  HEBREW,
  YHVH_PERMUTATIONS,
  ANA_BEKOACH,
  SHEM_72,
  jdToHebrew,
  getAnaBeKoachLine,
  getShem72,
  
  // Unified
  computePosition,
  computePhaseVector,
  DivinationOracle
};
