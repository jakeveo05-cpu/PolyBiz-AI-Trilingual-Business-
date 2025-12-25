/**
 * Preset Vocabulary Lists for PolyBiz Learning Stage
 * Organized by HSK level, topic, and special categories
 */

import { VocabItem } from "./storage";

// HSK 1 - Basic (150 characters)
export const HSK1_BASIC: VocabItem[] = [
  { char: "我", pinyin: "wǒ", meaning: "I, me" },
  { char: "你", pinyin: "nǐ", meaning: "you" },
  { char: "他", pinyin: "tā", meaning: "he, him" },
  { char: "她", pinyin: "tā", meaning: "she, her" },
  { char: "们", pinyin: "men", meaning: "plural marker" },
  { char: "是", pinyin: "shì", meaning: "to be" },
  { char: "不", pinyin: "bù", meaning: "not, no" },
  { char: "有", pinyin: "yǒu", meaning: "to have" },
  { char: "这", pinyin: "zhè", meaning: "this" },
  { char: "那", pinyin: "nà", meaning: "that" },
  { char: "什", pinyin: "shén", meaning: "what" },
  { char: "么", pinyin: "me", meaning: "question particle" },
  { char: "好", pinyin: "hǎo", meaning: "good" },
  { char: "大", pinyin: "dà", meaning: "big" },
  { char: "小", pinyin: "xiǎo", meaning: "small" },
  { char: "多", pinyin: "duō", meaning: "many, much" },
  { char: "少", pinyin: "shǎo", meaning: "few, little" },
  { char: "一", pinyin: "yī", meaning: "one" },
  { char: "二", pinyin: "èr", meaning: "two" },
  { char: "三", pinyin: "sān", meaning: "three" },
  { char: "四", pinyin: "sì", meaning: "four" },
  { char: "五", pinyin: "wǔ", meaning: "five" },
  { char: "六", pinyin: "liù", meaning: "six" },
  { char: "七", pinyin: "qī", meaning: "seven" },
  { char: "八", pinyin: "bā", meaning: "eight" },
  { char: "九", pinyin: "jiǔ", meaning: "nine" },
  { char: "十", pinyin: "shí", meaning: "ten" },
  { char: "百", pinyin: "bǎi", meaning: "hundred" },
  { char: "千", pinyin: "qiān", meaning: "thousand" },
  { char: "万", pinyin: "wàn", meaning: "ten thousand" },
];

// Business Chinese
export const BUSINESS_VOCAB: VocabItem[] = [
  { char: "公", pinyin: "gōng", meaning: "public, company" },
  { char: "司", pinyin: "sī", meaning: "manage, company" },
  { char: "经", pinyin: "jīng", meaning: "pass through, manage" },
  { char: "理", pinyin: "lǐ", meaning: "manage, reason" },
  { char: "市", pinyin: "shì", meaning: "market, city" },
  { char: "场", pinyin: "chǎng", meaning: "field, market" },
  { char: "客", pinyin: "kè", meaning: "guest, customer" },
  { char: "户", pinyin: "hù", meaning: "household, customer" },
  { char: "合", pinyin: "hé", meaning: "combine, contract" },
  { char: "同", pinyin: "tóng", meaning: "same, together" },
  { char: "价", pinyin: "jià", meaning: "price" },
  { char: "格", pinyin: "gé", meaning: "standard, price" },
  { char: "利", pinyin: "lì", meaning: "profit, benefit" },
  { char: "润", pinyin: "rùn", meaning: "profit, moist" },
  { char: "投", pinyin: "tóu", meaning: "throw, invest" },
  { char: "资", pinyin: "zī", meaning: "capital, invest" },
  { char: "银", pinyin: "yín", meaning: "silver, bank" },
  { char: "行", pinyin: "háng", meaning: "row, bank" },
  { char: "贸", pinyin: "mào", meaning: "trade" },
  { char: "易", pinyin: "yì", meaning: "easy, trade" },
];

// IT & Technology
export const IT_VOCAB: VocabItem[] = [
  { char: "电", pinyin: "diàn", meaning: "electricity" },
  { char: "脑", pinyin: "nǎo", meaning: "brain, computer" },
  { char: "网", pinyin: "wǎng", meaning: "net, internet" },
  { char: "络", pinyin: "luò", meaning: "net, network" },
  { char: "软", pinyin: "ruǎn", meaning: "soft, software" },
  { char: "件", pinyin: "jiàn", meaning: "piece, software" },
  { char: "硬", pinyin: "yìng", meaning: "hard, hardware" },
  { char: "数", pinyin: "shù", meaning: "number, data" },
  { char: "据", pinyin: "jù", meaning: "according to, data" },
  { char: "程", pinyin: "chéng", meaning: "journey, program" },
  { char: "序", pinyin: "xù", meaning: "order, program" },
  { char: "代", pinyin: "dài", meaning: "generation, code" },
  { char: "码", pinyin: "mǎ", meaning: "code, number" },
  { char: "算", pinyin: "suàn", meaning: "calculate" },
  { char: "法", pinyin: "fǎ", meaning: "method, algorithm" },
  { char: "智", pinyin: "zhì", meaning: "wisdom, AI" },
  { char: "能", pinyin: "néng", meaning: "ability, AI" },
  { char: "云", pinyin: "yún", meaning: "cloud" },
  { char: "存", pinyin: "cún", meaning: "store, save" },
  { char: "储", pinyin: "chǔ", meaning: "store, storage" },
];

// Commonly Confused Characters
export const CONFUSING_CHARS: VocabItem[] = [
  { char: "己", pinyin: "jǐ", meaning: "self" },
  { char: "已", pinyin: "yǐ", meaning: "already" },
  { char: "巳", pinyin: "sì", meaning: "6th earthly branch" },
  { char: "土", pinyin: "tǔ", meaning: "earth, soil" },
  { char: "士", pinyin: "shì", meaning: "scholar" },
  { char: "干", pinyin: "gān", meaning: "dry, do" },
  { char: "千", pinyin: "qiān", meaning: "thousand" },
  { char: "于", pinyin: "yú", meaning: "at, in" },
  { char: "末", pinyin: "mò", meaning: "end" },
  { char: "未", pinyin: "wèi", meaning: "not yet" },
  { char: "日", pinyin: "rì", meaning: "sun, day" },
  { char: "曰", pinyin: "yuē", meaning: "say" },
  { char: "人", pinyin: "rén", meaning: "person" },
  { char: "入", pinyin: "rù", meaning: "enter" },
  { char: "大", pinyin: "dà", meaning: "big" },
  { char: "太", pinyin: "tài", meaning: "too, very" },
  { char: "天", pinyin: "tiān", meaning: "sky, day" },
  { char: "夫", pinyin: "fū", meaning: "husband" },
];

// Time & Date
export const TIME_VOCAB: VocabItem[] = [
  { char: "年", pinyin: "nián", meaning: "year" },
  { char: "月", pinyin: "yuè", meaning: "month, moon" },
  { char: "日", pinyin: "rì", meaning: "day, sun" },
  { char: "时", pinyin: "shí", meaning: "time, hour" },
  { char: "分", pinyin: "fēn", meaning: "minute, divide" },
  { char: "秒", pinyin: "miǎo", meaning: "second" },
  { char: "今", pinyin: "jīn", meaning: "today, now" },
  { char: "明", pinyin: "míng", meaning: "bright, tomorrow" },
  { char: "昨", pinyin: "zuó", meaning: "yesterday" },
  { char: "早", pinyin: "zǎo", meaning: "early, morning" },
  { char: "晚", pinyin: "wǎn", meaning: "late, evening" },
  { char: "周", pinyin: "zhōu", meaning: "week, cycle" },
  { char: "星", pinyin: "xīng", meaning: "star" },
  { char: "期", pinyin: "qī", meaning: "period, week" },
];

// Colors
export const COLOR_VOCAB: VocabItem[] = [
  { char: "红", pinyin: "hóng", meaning: "red" },
  { char: "黄", pinyin: "huáng", meaning: "yellow" },
  { char: "蓝", pinyin: "lán", meaning: "blue" },
  { char: "绿", pinyin: "lǜ", meaning: "green" },
  { char: "白", pinyin: "bái", meaning: "white" },
  { char: "黑", pinyin: "hēi", meaning: "black" },
  { char: "灰", pinyin: "huī", meaning: "gray" },
  { char: "紫", pinyin: "zǐ", meaning: "purple" },
  { char: "橙", pinyin: "chéng", meaning: "orange" },
  { char: "粉", pinyin: "fěn", meaning: "pink, powder" },
];

// Family
export const FAMILY_VOCAB: VocabItem[] = [
  { char: "家", pinyin: "jiā", meaning: "home, family" },
  { char: "父", pinyin: "fù", meaning: "father" },
  { char: "母", pinyin: "mǔ", meaning: "mother" },
  { char: "爸", pinyin: "bà", meaning: "dad" },
  { char: "妈", pinyin: "mā", meaning: "mom" },
  { char: "哥", pinyin: "gē", meaning: "older brother" },
  { char: "姐", pinyin: "jiě", meaning: "older sister" },
  { char: "弟", pinyin: "dì", meaning: "younger brother" },
  { char: "妹", pinyin: "mèi", meaning: "younger sister" },
  { char: "儿", pinyin: "ér", meaning: "son, child" },
  { char: "女", pinyin: "nǚ", meaning: "daughter, female" },
  { char: "爷", pinyin: "yé", meaning: "grandfather" },
  { char: "奶", pinyin: "nǎi", meaning: "grandmother" },
];

// Get preset by category
export function getPresetVocab(category: string): VocabItem[] {
  switch (category) {
    case "hsk1":
      return HSK1_BASIC;
    case "business":
      return BUSINESS_VOCAB;
    case "it":
      return IT_VOCAB;
    case "confusing":
      return CONFUSING_CHARS;
    case "time":
      return TIME_VOCAB;
    case "colors":
      return COLOR_VOCAB;
    case "family":
      return FAMILY_VOCAB;
    default:
      return HSK1_BASIC;
  }
}

// Get all categories
export const VOCAB_CATEGORIES = [
  { id: "hsk1", name: "HSK 1 Cơ bản", count: HSK1_BASIC.length },
  { id: "business", name: "Kinh doanh", count: BUSINESS_VOCAB.length },
  { id: "it", name: "Công nghệ IT", count: IT_VOCAB.length },
  { id: "confusing", name: "Dễ nhầm lẫn", count: CONFUSING_CHARS.length },
  { id: "time", name: "Thời gian", count: TIME_VOCAB.length },
  { id: "colors", name: "Màu sắc", count: COLOR_VOCAB.length },
  { id: "family", name: "Gia đình", count: FAMILY_VOCAB.length },
];
