/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * TIME SYSTEMS - Complete Multi-Calendar Implementation
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Integration of multiple calendar/time systems:
 * - Mayan: Tzolkin (260), Haab (365), Long Count, Calendar Round
 * - Vedic: Yuga cycles, Tithi (lunar day), Nakshatra (lunar mansion)
 * - Hebrew/Torah: 12 permutations, 42-letter name, 72-letter name
 * - Gregorian: Standard civil calendar
 * 
 * Features:
 * - Date conversion between systems
 * - LCM-based cycle detection
 * - Phase vector computation
 * - Resonance/alignment detection
 * 
 * @module TIME_SYSTEMS
 * @version 1.0.0
 */

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: CORE TIME TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface JulianDay {
  value: number;  // Days since noon Jan 1, 4713 BCE
}

export interface PhaseVector {
  time: JulianDay;
  phases: Map<string, number>;  // Cycle name → phase (0 to 2π)
  positions: Map<string, number>;  // Cycle name → position within cycle
}

export interface CycleAlignment {
  time: JulianDay;
  alignedCycles: string[];
  alignmentType: "exact" | "near";
  deviation: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: GREGORIAN CALENDAR
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Gregorian {
  
  export interface Date {
    year: number;
    month: number;   // 1-12
    day: number;     // 1-31
    hour?: number;
    minute?: number;
    second?: number;
  }
  
  export function isLeapYear(year: number): boolean {
    return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
  }
  
  export function daysInMonth(year: number, month: number): number {
    const days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    if (month === 2 && isLeapYear(year)) return 29;
    return days[month - 1];
  }
  
  export function toJulianDay(date: Date): JulianDay {
    const { year, month, day } = date;
    const hour = date.hour ?? 12;
    const minute = date.minute ?? 0;
    const second = date.second ?? 0;
    
    const a = Math.floor((14 - month) / 12);
    const y = year + 4800 - a;
    const m = month + 12 * a - 3;
    
    let jd = day + Math.floor((153 * m + 2) / 5) + 365 * y + 
             Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
    
    // Add fractional day
    jd += (hour - 12) / 24 + minute / 1440 + second / 86400;
    
    return { value: jd };
  }
  
  export function fromJulianDay(jd: JulianDay): Date {
    const Z = Math.floor(jd.value + 0.5);
    const F = jd.value + 0.5 - Z;
    
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
    
    const day = B - D - Math.floor(30.6001 * E);
    const month = E < 14 ? E - 1 : E - 13;
    const year = month > 2 ? C - 4716 : C - 4715;
    
    const fracDay = F * 24;
    const hour = Math.floor(fracDay);
    const minute = Math.floor((fracDay - hour) * 60);
    const second = Math.floor(((fracDay - hour) * 60 - minute) * 60);
    
    return { year, month, day, hour, minute, second };
  }
  
  export function dayOfYear(date: Date): number {
    let doy = date.day;
    for (let m = 1; m < date.month; m++) {
      doy += daysInMonth(date.year, m);
    }
    return doy;
  }
  
  export function dayOfWeek(jd: JulianDay): number {
    // 0 = Sunday, 1 = Monday, ...
    return Math.floor(jd.value + 1.5) % 7;
  }
  
  export const WEEKDAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: MAYAN CALENDAR
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Mayan {
  
  // Tzolkin: 260-day sacred calendar (13 numbers × 20 day names)
  export interface Tzolkin {
    number: number;   // 1-13
    daySign: number;  // 0-19
  }
  
  export const TZOLKIN_PERIOD = 260;
  
  export const DAY_SIGNS = [
    "Imix", "Ik", "Akbal", "Kan", "Chicchan",
    "Cimi", "Manik", "Lamat", "Muluc", "Oc",
    "Chuen", "Eb", "Ben", "Ix", "Men",
    "Cib", "Caban", "Etznab", "Cauac", "Ahau"
  ];
  
  // Haab: 365-day solar calendar (18 months × 20 days + 5 Wayeb days)
  export interface Haab {
    month: number;    // 0-18 (18 = Wayeb)
    day: number;      // 0-19 (0-4 for Wayeb)
  }
  
  export const HAAB_PERIOD = 365;
  
  export const HAAB_MONTHS = [
    "Pop", "Uo", "Zip", "Zotz", "Tzec",
    "Xul", "Yaxkin", "Mol", "Chen", "Yax",
    "Zac", "Ceh", "Mac", "Kankin", "Muan",
    "Pax", "Kayab", "Cumku", "Wayeb"
  ];
  
  // Calendar Round: combination of Tzolkin and Haab (52 Haab years)
  export const CALENDAR_ROUND = 18980;  // LCM(260, 365)
  
  // Long Count: days since creation date (August 11, 3114 BCE)
  export interface LongCount {
    baktun: number;   // 144000 days
    katun: number;    // 7200 days
    tun: number;      // 360 days
    uinal: number;    // 20 days
    kin: number;      // 1 day
  }
  
  // Mayan creation date in Julian Day
  export const CREATION_JD = 584283;  // August 11, 3114 BCE (GMT correlation)
  
  // Convert Julian Day to Long Count
  export function toLongCount(jd: JulianDay): LongCount {
    let days = Math.floor(jd.value) - CREATION_JD;
    
    const baktun = Math.floor(days / 144000);
    days %= 144000;
    
    const katun = Math.floor(days / 7200);
    days %= 7200;
    
    const tun = Math.floor(days / 360);
    days %= 360;
    
    const uinal = Math.floor(days / 20);
    const kin = days % 20;
    
    return { baktun, katun, tun, uinal, kin };
  }
  
  // Convert Long Count to Julian Day
  export function fromLongCount(lc: LongCount): JulianDay {
    const days = lc.baktun * 144000 + lc.katun * 7200 + 
                 lc.tun * 360 + lc.uinal * 20 + lc.kin;
    return { value: CREATION_JD + days };
  }
  
  // Convert Julian Day to Tzolkin
  export function toTzolkin(jd: JulianDay): Tzolkin {
    const days = Math.floor(jd.value) - CREATION_JD;
    
    // At creation: 4 Ahau (number=4, daySign=19)
    const number = ((days + 3) % 13) + 1;
    const daySign = (days + 19) % 20;
    
    return { number, daySign };
  }
  
  // Convert Julian Day to Haab
  export function toHaab(jd: JulianDay): Haab {
    const days = Math.floor(jd.value) - CREATION_JD;
    
    // At creation: 8 Cumku
    const haabDays = (days + 348) % 365;
    
    if (haabDays >= 360) {
      return { month: 18, day: haabDays - 360 };  // Wayeb
    }
    
    const month = Math.floor(haabDays / 20);
    const day = haabDays % 20;
    
    return { month, day };
  }
  
  // Format Long Count as string
  export function formatLongCount(lc: LongCount): string {
    return `${lc.baktun}.${lc.katun}.${lc.tun}.${lc.uinal}.${lc.kin}`;
  }
  
  // Format Tzolkin as string
  export function formatTzolkin(tz: Tzolkin): string {
    return `${tz.number} ${DAY_SIGNS[tz.daySign]}`;
  }
  
  // Format Haab as string
  export function formatHaab(haab: Haab): string {
    return `${haab.day} ${HAAB_MONTHS[haab.month]}`;
  }
  
  // Get complete Mayan date
  export function getFullDate(jd: JulianDay): {
    longCount: LongCount;
    tzolkin: Tzolkin;
    haab: Haab;
  } {
    return {
      longCount: toLongCount(jd),
      tzolkin: toTzolkin(jd),
      haab: toHaab(jd)
    };
  }
  
  // Calculate days until next Calendar Round alignment
  export function daysToNextCalendarRound(jd: JulianDay): number {
    const daysSinceCreation = Math.floor(jd.value) - CREATION_JD;
    const positionInRound = daysSinceCreation % CALENDAR_ROUND;
    return CALENDAR_ROUND - positionInRound;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: VEDIC CALENDAR
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Vedic {
  
  // Yuga cycle (4 ages in ratio 4:3:2:1)
  export interface Yuga {
    name: YugaName;
    year: number;        // Year within yuga
    totalYears: number;  // Total years in this yuga
    dharmaFactor: number; // Virtue/dharma level (4/10 to 1/10)
  }
  
  export type YugaName = "Satya" | "Treta" | "Dwapara" | "Kali";
  
  // Yuga durations in divine years
  export const YUGA_YEARS = {
    Satya: 1728000,
    Treta: 1296000,
    Dwapara: 864000,
    Kali: 432000
  };
  
  export const MAHAYUGA = 4320000;  // Sum of all yugas
  
  // Current Kali Yuga started Feb 18, 3102 BCE (Julian Day 588466)
  export const KALI_YUGA_START_JD = 588466;
  
  // Tithi: lunar day (30 per lunar month)
  export interface Tithi {
    number: number;  // 1-30
    paksha: "Shukla" | "Krishna";  // Bright/Dark fortnight
    name: string;
  }
  
  export const TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
  ];
  
  // Nakshatra: lunar mansion (27 divisions of ecliptic)
  export interface Nakshatra {
    number: number;  // 1-27
    name: string;
    deity: string;
  }
  
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
    { name: "Chitra", deity: "Tvashtar" },
    { name: "Swati", deity: "Vayu" },
    { name: "Vishakha", deity: "Indra-Agni" },
    { name: "Anuradha", deity: "Mitra" },
    { name: "Jyeshtha", deity: "Indra" },
    { name: "Mula", deity: "Nirriti" },
    { name: "Purva Ashadha", deity: "Apas" },
    { name: "Uttara Ashadha", deity: "Vishvadevas" },
    { name: "Shravana", deity: "Vishnu" },
    { name: "Dhanishta", deity: "Vasus" },
    { name: "Shatabhisha", deity: "Varuna" },
    { name: "Purva Bhadrapada", deity: "Aja Ekapada" },
    { name: "Uttara Bhadrapada", deity: "Ahir Budhnya" },
    { name: "Revati", deity: "Pushan" }
  ];
  
  // Get current Yuga position
  export function getCurrentYuga(jd: JulianDay): Yuga {
    const yearsSinceKali = (jd.value - KALI_YUGA_START_JD) / 365.25;
    
    // We're in Kali Yuga
    return {
      name: "Kali",
      year: Math.floor(yearsSinceKali),
      totalYears: YUGA_YEARS.Kali,
      dharmaFactor: 0.25  // 1/4 dharma in Kali Yuga
    };
  }
  
  // Approximate Tithi from Julian Day
  export function getTithi(jd: JulianDay): Tithi {
    // Synodic month = 29.530588853 days
    const SYNODIC_MONTH = 29.530588853;
    
    // New moon reference: Jan 6, 2000 (JD 2451550.1)
    const REF_NEW_MOON = 2451550.1;
    
    const daysSinceNewMoon = (jd.value - REF_NEW_MOON) % SYNODIC_MONTH;
    const tithiNumber = Math.floor(daysSinceNewMoon / (SYNODIC_MONTH / 30)) + 1;
    
    const paksha = tithiNumber <= 15 ? "Shukla" : "Krishna";
    const displayNumber = tithiNumber <= 15 ? tithiNumber : tithiNumber - 15;
    
    return {
      number: tithiNumber,
      paksha,
      name: TITHI_NAMES[(displayNumber - 1) % 15]
    };
  }
  
  // Approximate Nakshatra from Julian Day
  export function getNakshatra(jd: JulianDay): Nakshatra {
    // Sidereal month = 27.321661 days
    const SIDEREAL_MONTH = 27.321661;
    
    // Reference: Moon at Ashwini start
    const REF_ASHWINI = 2451545.0;
    
    const daysSinceRef = (jd.value - REF_ASHWINI) % SIDEREAL_MONTH;
    const nakshatraNum = Math.floor(daysSinceRef / (SIDEREAL_MONTH / 27)) + 1;
    
    const info = NAKSHATRAS[(nakshatraNum - 1) % 27];
    
    return {
      number: nakshatraNum,
      name: info.name,
      deity: info.deity
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: HEBREW CALENDAR
// ═══════════════════════════════════════════════════════════════════════════════

export namespace Hebrew {
  
  // Hebrew months
  export const MONTHS = [
    "Nisan", "Iyyar", "Sivan", "Tammuz", "Av", "Elul",
    "Tishrei", "Cheshvan", "Kislev", "Tevet", "Shevat", "Adar"
  ];
  
  // 12 permutations of YHVH for 12 months
  export const YHVH_PERMUTATIONS = [
    "YHVH", "YHHV", "YVHH", "HVHY", "HVYH", "HHVY",
    "VHHY", "VHYH", "VYHH", "HYVH", "HYHV", "HHYV"
  ];
  
  // 42-letter divine name (Ana BeKoach)
  export const NAME_42 = [
    "אבג יתץ",
    "קרע שטן",
    "נגד יכש",
    "בטר צתג",
    "חקב טנע",
    "יגל פזק",
    "שקו צית"
  ];
  
  // Get permutation for month
  export function getMonthPermutation(month: number): string {
    return YHVH_PERMUTATIONS[(month - 1) % 12];
  }
  
  // Get 42-name line for day of week
  export function get42NameLine(dayOfWeek: number): string {
    return NAME_42[dayOfWeek % 7];
  }
  
  // Hebrew date interface
  export interface HebrewDate {
    year: number;
    month: number;
    day: number;
    monthName: string;
  }
  
  // Approximate Hebrew year from Julian Day
  export function getHebrewYear(jd: JulianDay): number {
    // Hebrew calendar epoch: Oct 7, 3761 BCE (JD 347998)
    const HEBREW_EPOCH = 347998;
    const yearsSinceEpoch = (jd.value - HEBREW_EPOCH) / 365.25;
    return Math.floor(yearsSinceEpoch) + 1;
  }
  
  // Get Hebrew month (approximate)
  export function getHebrewMonth(jd: JulianDay): number {
    const greg = Gregorian.fromJulianDay(jd);
    // Nisan starts around March/April
    // Simple approximation: offset by 6 months from Gregorian
    return ((greg.month + 5) % 12) + 1;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 6: PHASE VECTOR SYSTEM
// ═══════════════════════════════════════════════════════════════════════════════

export namespace PhaseSystem {
  
  export interface Cycle {
    id: string;
    name: string;
    period: number;  // In days
    epoch: number;   // Julian Day of epoch
    description: string;
  }
  
  // Standard cycles
  export const CYCLES: Cycle[] = [
    { id: "week", name: "Week", period: 7, epoch: 0, description: "7-day week" },
    { id: "tzolkin", name: "Tzolkin", period: 260, epoch: Mayan.CREATION_JD, description: "Mayan sacred calendar" },
    { id: "haab", name: "Haab", period: 365, epoch: Mayan.CREATION_JD, description: "Mayan solar calendar" },
    { id: "synodic", name: "Synodic Month", period: 29.530588853, epoch: 2451550.1, description: "Lunar phase cycle" },
    { id: "sidereal", name: "Sidereal Month", period: 27.321661, epoch: 2451545.0, description: "Moon through zodiac" },
    { id: "solar", name: "Solar Year", period: 365.2422, epoch: 2451545.0, description: "Tropical year" },
    { id: "calendar_round", name: "Calendar Round", period: Mayan.CALENDAR_ROUND, epoch: Mayan.CREATION_JD, description: "Mayan 52-year cycle" }
  ];
  
  // Compute position within cycle
  export function cyclePosition(cycle: Cycle, jd: JulianDay): number {
    const elapsed = jd.value - cycle.epoch;
    return ((elapsed % cycle.period) + cycle.period) % cycle.period;
  }
  
  // Compute phase (0 to 2π)
  export function cyclePhase(cycle: Cycle, jd: JulianDay): number {
    const pos = cyclePosition(cycle, jd);
    return (2 * Math.PI * pos) / cycle.period;
  }
  
  // Compute phase vector for all cycles
  export function computePhaseVector(jd: JulianDay, cycleIds?: string[]): PhaseVector {
    const phases = new Map<string, number>();
    const positions = new Map<string, number>();
    
    const cyclesToUse = cycleIds 
      ? CYCLES.filter(c => cycleIds.includes(c.id))
      : CYCLES;
    
    for (const cycle of cyclesToUse) {
      phases.set(cycle.id, cyclePhase(cycle, jd));
      positions.set(cycle.id, cyclePosition(cycle, jd));
    }
    
    return { time: jd, phases, positions };
  }
  
  // Compute GCD of two numbers
  function gcd(a: number, b: number): number {
    a = Math.round(a);
    b = Math.round(b);
    while (b !== 0) {
      const t = b;
      b = a % b;
      a = t;
    }
    return a;
  }
  
  // Compute LCM of two numbers
  function lcm(a: number, b: number): number {
    return Math.abs(Math.round(a) * Math.round(b)) / gcd(a, b);
  }
  
  // Compute LCM of multiple cycles
  export function cycleLCM(cycleIds: string[]): number {
    const cycles = cycleIds.map(id => CYCLES.find(c => c.id === id)).filter(Boolean) as Cycle[];
    if (cycles.length === 0) return 0;
    
    return cycles.reduce((acc, c) => lcm(acc, c.period), 1);
  }
  
  // Find next alignment of multiple cycles
  export function findNextAlignment(
    jd: JulianDay,
    cycleIds: string[],
    tolerance: number = 0.5  // Days
  ): CycleAlignment | null {
    const period = cycleLCM(cycleIds);
    if (period === 0) return null;
    
    const cycles = cycleIds.map(id => CYCLES.find(c => c.id === id)).filter(Boolean) as Cycle[];
    
    // Search for alignment
    for (let offset = 1; offset <= period; offset++) {
      const testJd: JulianDay = { value: jd.value + offset };
      
      let allAligned = true;
      let maxDeviation = 0;
      
      for (const cycle of cycles) {
        const pos = cyclePosition(cycle, testJd);
        const deviation = Math.min(pos, cycle.period - pos);
        
        if (deviation > tolerance) {
          allAligned = false;
          break;
        }
        
        maxDeviation = Math.max(maxDeviation, deviation);
      }
      
      if (allAligned) {
        return {
          time: testJd,
          alignedCycles: cycleIds,
          alignmentType: maxDeviation < 0.1 ? "exact" : "near",
          deviation: maxDeviation
        };
      }
    }
    
    return null;
  }
  
  // Phase vector distance (on torus)
  export function phaseDistance(v1: PhaseVector, v2: PhaseVector): number {
    let sumSq = 0;
    
    for (const [cycleId, phase1] of v1.phases) {
      const phase2 = v2.phases.get(cycleId);
      if (phase2 !== undefined) {
        // Toroidal distance
        let diff = Math.abs(phase1 - phase2);
        diff = Math.min(diff, 2 * Math.PI - diff);
        sumSq += diff * diff;
      }
    }
    
    return Math.sqrt(sumSq);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 7: UNIFIED TIME ORACLE
// ═══════════════════════════════════════════════════════════════════════════════

export interface OracleQuery {
  gregorianDate?: Gregorian.Date;
  julianDay?: JulianDay;
  systems?: ("mayan" | "vedic" | "hebrew" | "gregorian")[];
}

export interface OracleResult {
  julianDay: JulianDay;
  gregorian: Gregorian.Date;
  mayan?: {
    longCount: Mayan.LongCount;
    tzolkin: Mayan.Tzolkin;
    haab: Mayan.Haab;
    calendarRoundPosition: number;
  };
  vedic?: {
    yuga: Vedic.Yuga;
    tithi: Vedic.Tithi;
    nakshatra: Vedic.Nakshatra;
  };
  hebrew?: {
    year: number;
    month: number;
    permutation: string;
    name42Line: string;
  };
  phaseVector: PhaseVector;
  upcomingAlignments: CycleAlignment[];
}

export class TimeOracle {
  
  query(query: OracleQuery): OracleResult {
    // Determine Julian Day
    let jd: JulianDay;
    if (query.julianDay) {
      jd = query.julianDay;
    } else if (query.gregorianDate) {
      jd = Gregorian.toJulianDay(query.gregorianDate);
    } else {
      // Default to now
      const now = new Date();
      jd = Gregorian.toJulianDay({
        year: now.getFullYear(),
        month: now.getMonth() + 1,
        day: now.getDate(),
        hour: now.getHours(),
        minute: now.getMinutes(),
        second: now.getSeconds()
      });
    }
    
    const systems = query.systems ?? ["mayan", "vedic", "hebrew", "gregorian"];
    const result: OracleResult = {
      julianDay: jd,
      gregorian: Gregorian.fromJulianDay(jd),
      phaseVector: PhaseSystem.computePhaseVector(jd),
      upcomingAlignments: []
    };
    
    if (systems.includes("mayan")) {
      const mayanDate = Mayan.getFullDate(jd);
      result.mayan = {
        ...mayanDate,
        calendarRoundPosition: (Math.floor(jd.value) - Mayan.CREATION_JD) % Mayan.CALENDAR_ROUND
      };
    }
    
    if (systems.includes("vedic")) {
      result.vedic = {
        yuga: Vedic.getCurrentYuga(jd),
        tithi: Vedic.getTithi(jd),
        nakshatra: Vedic.getNakshatra(jd)
      };
    }
    
    if (systems.includes("hebrew")) {
      const dayOfWeek = Gregorian.dayOfWeek(jd);
      const month = Hebrew.getHebrewMonth(jd);
      result.hebrew = {
        year: Hebrew.getHebrewYear(jd),
        month,
        permutation: Hebrew.getMonthPermutation(month),
        name42Line: Hebrew.get42NameLine(dayOfWeek)
      };
    }
    
    // Find upcoming alignments
    const tzolkinHaab = PhaseSystem.findNextAlignment(jd, ["tzolkin", "haab"], 1);
    if (tzolkinHaab) {
      result.upcomingAlignments.push(tzolkinHaab);
    }
    
    return result;
  }
  
  // Format result as string
  formatResult(result: OracleResult): string {
    const lines: string[] = [];
    
    lines.push(`=== TIME ORACLE RESULT ===`);
    lines.push(`Julian Day: ${result.julianDay.value.toFixed(5)}`);
    lines.push(`Gregorian: ${result.gregorian.year}-${result.gregorian.month.toString().padStart(2, '0')}-${result.gregorian.day.toString().padStart(2, '0')}`);
    lines.push(`Day of Week: ${Gregorian.WEEKDAY_NAMES[Gregorian.dayOfWeek(result.julianDay)]}`);
    
    if (result.mayan) {
      lines.push(`\n--- Mayan ---`);
      lines.push(`Long Count: ${Mayan.formatLongCount(result.mayan.longCount)}`);
      lines.push(`Tzolkin: ${Mayan.formatTzolkin(result.mayan.tzolkin)}`);
      lines.push(`Haab: ${Mayan.formatHaab(result.mayan.haab)}`);
      lines.push(`Calendar Round Position: ${result.mayan.calendarRoundPosition} / ${Mayan.CALENDAR_ROUND}`);
    }
    
    if (result.vedic) {
      lines.push(`\n--- Vedic ---`);
      lines.push(`Yuga: ${result.vedic.yuga.name} (Year ${result.vedic.yuga.year})`);
      lines.push(`Dharma Factor: ${result.vedic.yuga.dharmaFactor * 100}%`);
      lines.push(`Tithi: ${result.vedic.tithi.paksha} ${result.vedic.tithi.name}`);
      lines.push(`Nakshatra: ${result.vedic.nakshatra.name} (${result.vedic.nakshatra.deity})`);
    }
    
    if (result.hebrew) {
      lines.push(`\n--- Hebrew ---`);
      lines.push(`Year: ${result.hebrew.year} AM`);
      lines.push(`YHVH Permutation: ${result.hebrew.permutation}`);
      lines.push(`42-Name Line: ${result.hebrew.name42Line}`);
    }
    
    if (result.upcomingAlignments.length > 0) {
      lines.push(`\n--- Upcoming Alignments ---`);
      for (const align of result.upcomingAlignments) {
        const daysAway = align.time.value - result.julianDay.value;
        lines.push(`${align.alignedCycles.join(" + ")}: ${daysAway.toFixed(0)} days (${align.alignmentType})`);
      }
    }
    
    return lines.join('\n');
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  Gregorian,
  Mayan,
  Vedic,
  Hebrew,
  PhaseSystem,
  TimeOracle
};
