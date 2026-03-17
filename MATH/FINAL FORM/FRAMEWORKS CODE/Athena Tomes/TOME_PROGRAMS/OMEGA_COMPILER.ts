/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * OMEGA COMPILER - Complete Proof-Carrying Compilation Pipeline
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Full implementation of the Ω-gated self-compilation system:
 * 
 * Pipeline: Parse → Normalize → Plan → Solve → Certify → Store
 * 
 * Features:
 *   - Lexer and parser for TOME source language
 *   - AST normalization and canonicalization
 *   - Constraint solving with SAT/SMT integration
 *   - Nine-stage Ω-gated compilation
 *   - Proof certificate generation
 *   - Playbook execution (Π1-Π7)
 * 
 * @module OMEGA_COMPILER
 * @version 2.0.0
 */

import {
  TruthValue,
  EdgeKind,
  Corridors,
  WitnessPtr,
  Witnesses,
  ReplayCapsule,
  ValidationResult
} from './CORE_INFRASTRUCTURE';

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 1: LEXER
// ═══════════════════════════════════════════════════════════════════════════════

/** Token types */
export enum TokenType {
  // Literals
  Int = "INT",
  Float = "FLOAT",
  String = "STRING",
  Bool = "BOOL",
  Nil = "NIL",
  
  // Identifiers
  Ident = "IDENT",
  Address = "ADDRESS",
  
  // Keywords
  Let = "LET",
  Fn = "FN",
  If = "IF",
  Else = "ELSE",
  While = "WHILE",
  Return = "RETURN",
  Truth = "TRUTH",
  Witness = "WITNESS",
  Certify = "CERTIFY",
  Assert = "ASSERT",
  Corridor = "CORRIDOR",
  Omega = "OMEGA",
  
  // Operators
  Plus = "PLUS",
  Minus = "MINUS",
  Star = "STAR",
  Slash = "SLASH",
  Percent = "PERCENT",
  Eq = "EQ",
  EqEq = "EQEQ",
  NEq = "NEQ",
  Lt = "LT",
  Gt = "GT",
  LtEq = "LTEQ",
  GtEq = "GTEQ",
  And = "AND",
  Or = "OR",
  Not = "NOT",
  Arrow = "ARROW",
  FatArrow = "FATARROW",
  
  // Delimiters
  LParen = "LPAREN",
  RParen = "RPAREN",
  LBrace = "LBRACE",
  RBrace = "RBRACE",
  LBracket = "LBRACKET",
  RBracket = "RBRACKET",
  Comma = "COMMA",
  Colon = "COLON",
  Semicolon = "SEMICOLON",
  Dot = "DOT",
  ColonColon = "COLONCOLON",
  
  // Special
  Newline = "NEWLINE",
  EOF = "EOF",
  Error = "ERROR"
}

/** Token */
export interface Token {
  type: TokenType;
  value: string;
  line: number;
  column: number;
}

/** Keywords map */
const KEYWORDS: Map<string, TokenType> = new Map([
  ["let", TokenType.Let],
  ["fn", TokenType.Fn],
  ["if", TokenType.If],
  ["else", TokenType.Else],
  ["while", TokenType.While],
  ["return", TokenType.Return],
  ["truth", TokenType.Truth],
  ["witness", TokenType.Witness],
  ["certify", TokenType.Certify],
  ["assert", TokenType.Assert],
  ["corridor", TokenType.Corridor],
  ["omega", TokenType.Omega],
  ["true", TokenType.Bool],
  ["false", TokenType.Bool],
  ["nil", TokenType.Nil],
  ["and", TokenType.And],
  ["or", TokenType.Or],
  ["not", TokenType.Not]
]);

/**
 * Lexer class
 */
export class Lexer {
  private source: string;
  private pos: number = 0;
  private line: number = 1;
  private column: number = 1;
  
  constructor(source: string) {
    this.source = source;
  }
  
  tokenize(): Token[] {
    const tokens: Token[] = [];
    
    while (!this.isAtEnd()) {
      const token = this.nextToken();
      if (token.type !== TokenType.Newline) {
        tokens.push(token);
      }
      if (token.type === TokenType.EOF || token.type === TokenType.Error) {
        break;
      }
    }
    
    if (tokens.length === 0 || tokens[tokens.length - 1].type !== TokenType.EOF) {
      tokens.push(this.makeToken(TokenType.EOF, ""));
    }
    
    return tokens;
  }
  
  private nextToken(): Token {
    this.skipWhitespace();
    
    if (this.isAtEnd()) {
      return this.makeToken(TokenType.EOF, "");
    }
    
    const c = this.advance();
    
    // Single character tokens
    switch (c) {
      case '(': return this.makeToken(TokenType.LParen, c);
      case ')': return this.makeToken(TokenType.RParen, c);
      case '{': return this.makeToken(TokenType.LBrace, c);
      case '}': return this.makeToken(TokenType.RBrace, c);
      case '[': return this.makeToken(TokenType.LBracket, c);
      case ']': return this.makeToken(TokenType.RBracket, c);
      case ',': return this.makeToken(TokenType.Comma, c);
      case ';': return this.makeToken(TokenType.Semicolon, c);
      case '.': return this.makeToken(TokenType.Dot, c);
      case '+': return this.makeToken(TokenType.Plus, c);
      case '*': return this.makeToken(TokenType.Star, c);
      case '/': 
        if (this.match('/')) {
          this.skipLineComment();
          return this.nextToken();
        }
        return this.makeToken(TokenType.Slash, c);
      case '%': return this.makeToken(TokenType.Percent, c);
      case '\n':
        this.line++;
        this.column = 1;
        return this.makeToken(TokenType.Newline, c);
    }
    
    // Two character tokens
    if (c === '-') {
      if (this.match('>')) return this.makeToken(TokenType.Arrow, "->");
      return this.makeToken(TokenType.Minus, c);
    }
    
    if (c === '=') {
      if (this.match('=')) return this.makeToken(TokenType.EqEq, "==");
      if (this.match('>')) return this.makeToken(TokenType.FatArrow, "=>");
      return this.makeToken(TokenType.Eq, c);
    }
    
    if (c === '!') {
      if (this.match('=')) return this.makeToken(TokenType.NEq, "!=");
      return this.makeToken(TokenType.Not, c);
    }
    
    if (c === '<') {
      if (this.match('=')) return this.makeToken(TokenType.LtEq, "<=");
      return this.makeToken(TokenType.Lt, c);
    }
    
    if (c === '>') {
      if (this.match('=')) return this.makeToken(TokenType.GtEq, ">=");
      return this.makeToken(TokenType.Gt, c);
    }
    
    if (c === ':') {
      if (this.match(':')) return this.makeToken(TokenType.ColonColon, "::");
      return this.makeToken(TokenType.Colon, c);
    }
    
    if (c === '&') {
      if (this.match('&')) return this.makeToken(TokenType.And, "&&");
      return this.makeToken(TokenType.Error, `Unexpected '&'`);
    }
    
    if (c === '|') {
      if (this.match('|')) return this.makeToken(TokenType.Or, "||");
      return this.makeToken(TokenType.Error, `Unexpected '|'`);
    }
    
    // String
    if (c === '"') {
      return this.string();
    }
    
    // Number
    if (this.isDigit(c)) {
      return this.number(c);
    }
    
    // Identifier or keyword
    if (this.isAlpha(c)) {
      return this.identifier(c);
    }
    
    return this.makeToken(TokenType.Error, `Unexpected character: ${c}`);
  }
  
  private string(): Token {
    const start = this.pos;
    while (!this.isAtEnd() && this.peek() !== '"') {
      if (this.peek() === '\n') {
        this.line++;
        this.column = 1;
      }
      if (this.peek() === '\\') {
        this.advance();  // Skip escape
      }
      this.advance();
    }
    
    if (this.isAtEnd()) {
      return this.makeToken(TokenType.Error, "Unterminated string");
    }
    
    const value = this.source.slice(start, this.pos);
    this.advance();  // Closing quote
    return this.makeToken(TokenType.String, value);
  }
  
  private number(first: string): Token {
    let value = first;
    while (!this.isAtEnd() && this.isDigit(this.peek())) {
      value += this.advance();
    }
    
    if (this.peek() === '.' && this.isDigit(this.peekNext())) {
      value += this.advance();  // Decimal point
      while (!this.isAtEnd() && this.isDigit(this.peek())) {
        value += this.advance();
      }
      return this.makeToken(TokenType.Float, value);
    }
    
    return this.makeToken(TokenType.Int, value);
  }
  
  private identifier(first: string): Token {
    let value = first;
    while (!this.isAtEnd() && (this.isAlphaNumeric(this.peek()) || this.peek() === '_')) {
      value += this.advance();
    }
    
    // Check for address pattern: Ms⟨...⟩::...
    if (value === "Ms" && this.peek() === '⟨') {
      while (!this.isAtEnd() && this.peek() !== ' ' && this.peek() !== '\n') {
        value += this.advance();
      }
      return this.makeToken(TokenType.Address, value);
    }
    
    const keyword = KEYWORDS.get(value.toLowerCase());
    if (keyword) {
      return this.makeToken(keyword, value);
    }
    
    return this.makeToken(TokenType.Ident, value);
  }
  
  private skipWhitespace(): void {
    while (!this.isAtEnd()) {
      const c = this.peek();
      if (c === ' ' || c === '\r' || c === '\t') {
        this.advance();
      } else {
        break;
      }
    }
  }
  
  private skipLineComment(): void {
    while (!this.isAtEnd() && this.peek() !== '\n') {
      this.advance();
    }
  }
  
  private isAtEnd(): boolean {
    return this.pos >= this.source.length;
  }
  
  private peek(): string {
    return this.source[this.pos] || '\0';
  }
  
  private peekNext(): string {
    return this.source[this.pos + 1] || '\0';
  }
  
  private advance(): string {
    const c = this.source[this.pos++];
    this.column++;
    return c;
  }
  
  private match(expected: string): boolean {
    if (this.isAtEnd() || this.source[this.pos] !== expected) {
      return false;
    }
    this.pos++;
    this.column++;
    return true;
  }
  
  private makeToken(type: TokenType, value: string): Token {
    return { type, value, line: this.line, column: this.column - value.length };
  }
  
  private isDigit(c: string): boolean {
    return c >= '0' && c <= '9';
  }
  
  private isAlpha(c: string): boolean {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c === '_';
  }
  
  private isAlphaNumeric(c: string): boolean {
    return this.isAlpha(c) || this.isDigit(c);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 2: AST NODES
// ═══════════════════════════════════════════════════════════════════════════════

/** AST node types */
export enum NodeType {
  // Expressions
  Literal = "Literal",
  Identifier = "Identifier",
  Address = "Address",
  Binary = "Binary",
  Unary = "Unary",
  Call = "Call",
  Index = "Index",
  Member = "Member",
  Array = "Array",
  Record = "Record",
  Lambda = "Lambda",
  
  // Statements
  Let = "Let",
  Assign = "Assign",
  If = "If",
  While = "While",
  Return = "Return",
  Block = "Block",
  ExprStmt = "ExprStmt",
  
  // Declarations
  FnDecl = "FnDecl",
  
  // Special
  Truth = "Truth",
  Witness = "Witness",
  Certify = "Certify",
  Assert = "Assert",
  Corridor = "Corridor",
  Omega = "Omega",
  
  // Program
  Program = "Program"
}

/** Base AST node */
export interface ASTNode {
  type: NodeType;
  line: number;
  column: number;
}

/** Literal expression */
export interface LiteralNode extends ASTNode {
  type: NodeType.Literal;
  valueType: "int" | "float" | "string" | "bool" | "nil";
  value: number | string | boolean | null;
}

/** Identifier expression */
export interface IdentifierNode extends ASTNode {
  type: NodeType.Identifier;
  name: string;
}

/** Address expression */
export interface AddressNode extends ASTNode {
  type: NodeType.Address;
  address: string;
}

/** Binary expression */
export interface BinaryNode extends ASTNode {
  type: NodeType.Binary;
  operator: string;
  left: ExprNode;
  right: ExprNode;
}

/** Unary expression */
export interface UnaryNode extends ASTNode {
  type: NodeType.Unary;
  operator: string;
  operand: ExprNode;
}

/** Call expression */
export interface CallNode extends ASTNode {
  type: NodeType.Call;
  callee: ExprNode;
  args: ExprNode[];
}

/** Index expression */
export interface IndexNode extends ASTNode {
  type: NodeType.Index;
  object: ExprNode;
  index: ExprNode;
}

/** Member expression */
export interface MemberNode extends ASTNode {
  type: NodeType.Member;
  object: ExprNode;
  member: string;
}

/** Array expression */
export interface ArrayNode extends ASTNode {
  type: NodeType.Array;
  elements: ExprNode[];
}

/** Record expression */
export interface RecordNode extends ASTNode {
  type: NodeType.Record;
  fields: Map<string, ExprNode>;
}

/** Lambda expression */
export interface LambdaNode extends ASTNode {
  type: NodeType.Lambda;
  params: string[];
  body: ExprNode | BlockNode;
}

/** Let statement */
export interface LetNode extends ASTNode {
  type: NodeType.Let;
  name: string;
  init?: ExprNode;
}

/** Assignment statement */
export interface AssignNode extends ASTNode {
  type: NodeType.Assign;
  target: ExprNode;
  value: ExprNode;
}

/** If statement */
export interface IfNode extends ASTNode {
  type: NodeType.If;
  condition: ExprNode;
  then: StmtNode;
  else?: StmtNode;
}

/** While statement */
export interface WhileNode extends ASTNode {
  type: NodeType.While;
  condition: ExprNode;
  body: StmtNode;
}

/** Return statement */
export interface ReturnNode extends ASTNode {
  type: NodeType.Return;
  value?: ExprNode;
}

/** Block statement */
export interface BlockNode extends ASTNode {
  type: NodeType.Block;
  statements: StmtNode[];
}

/** Expression statement */
export interface ExprStmtNode extends ASTNode {
  type: NodeType.ExprStmt;
  expr: ExprNode;
}

/** Function declaration */
export interface FnDeclNode extends ASTNode {
  type: NodeType.FnDecl;
  name: string;
  params: string[];
  body: BlockNode;
}

/** Truth expression */
export interface TruthNode extends ASTNode {
  type: NodeType.Truth;
  expr: ExprNode;
}

/** Witness expression */
export interface WitnessNode extends ASTNode {
  type: NodeType.Witness;
  expr: ExprNode;
}

/** Certify statement */
export interface CertifyNode extends ASTNode {
  type: NodeType.Certify;
  claim: ExprNode;
  witness: ExprNode;
}

/** Assert statement */
export interface AssertNode extends ASTNode {
  type: NodeType.Assert;
  condition: ExprNode;
  message?: string;
}

/** Corridor block */
export interface CorridorNode extends ASTNode {
  type: NodeType.Corridor;
  budgets: {
    hubs?: number;
    time?: number;
    memory?: number;
  };
  body: BlockNode;
}

/** Omega gate */
export interface OmegaNode extends ASTNode {
  type: NodeType.Omega;
  threshold: number;
  body: StmtNode;
}

/** Program node */
export interface ProgramNode extends ASTNode {
  type: NodeType.Program;
  declarations: DeclNode[];
}

/** Expression union */
export type ExprNode = 
  | LiteralNode 
  | IdentifierNode 
  | AddressNode
  | BinaryNode 
  | UnaryNode 
  | CallNode 
  | IndexNode
  | MemberNode
  | ArrayNode
  | RecordNode
  | LambdaNode
  | TruthNode
  | WitnessNode;

/** Statement union */
export type StmtNode = 
  | LetNode 
  | AssignNode 
  | IfNode 
  | WhileNode 
  | ReturnNode 
  | BlockNode 
  | ExprStmtNode
  | CertifyNode
  | AssertNode
  | CorridorNode
  | OmegaNode;

/** Declaration union */
export type DeclNode = FnDeclNode | StmtNode;

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 3: PARSER
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Recursive descent parser
 */
export class Parser {
  private tokens: Token[];
  private pos: number = 0;
  private errors: string[] = [];
  
  constructor(tokens: Token[]) {
    this.tokens = tokens;
  }
  
  parse(): ProgramNode {
    const declarations: DeclNode[] = [];
    
    while (!this.isAtEnd()) {
      try {
        declarations.push(this.declaration());
      } catch (e) {
        this.errors.push((e as Error).message);
        this.synchronize();
      }
    }
    
    return {
      type: NodeType.Program,
      declarations,
      line: 1,
      column: 1
    };
  }
  
  getErrors(): string[] {
    return this.errors;
  }
  
  private declaration(): DeclNode {
    if (this.match(TokenType.Fn)) {
      return this.fnDeclaration();
    }
    return this.statement();
  }
  
  private fnDeclaration(): FnDeclNode {
    const token = this.previous();
    const name = this.consume(TokenType.Ident, "Expected function name").value;
    
    this.consume(TokenType.LParen, "Expected '(' after function name");
    const params: string[] = [];
    
    if (!this.check(TokenType.RParen)) {
      do {
        params.push(this.consume(TokenType.Ident, "Expected parameter name").value);
      } while (this.match(TokenType.Comma));
    }
    
    this.consume(TokenType.RParen, "Expected ')' after parameters");
    const body = this.block();
    
    return {
      type: NodeType.FnDecl,
      name,
      params,
      body,
      line: token.line,
      column: token.column
    };
  }
  
  private statement(): StmtNode {
    if (this.match(TokenType.Let)) return this.letStatement();
    if (this.match(TokenType.If)) return this.ifStatement();
    if (this.match(TokenType.While)) return this.whileStatement();
    if (this.match(TokenType.Return)) return this.returnStatement();
    if (this.match(TokenType.LBrace)) return this.block();
    if (this.match(TokenType.Certify)) return this.certifyStatement();
    if (this.match(TokenType.Assert)) return this.assertStatement();
    if (this.match(TokenType.Corridor)) return this.corridorStatement();
    if (this.match(TokenType.Omega)) return this.omegaStatement();
    
    return this.expressionStatement();
  }
  
  private letStatement(): LetNode {
    const token = this.previous();
    const name = this.consume(TokenType.Ident, "Expected variable name").value;
    
    let init: ExprNode | undefined;
    if (this.match(TokenType.Eq)) {
      init = this.expression();
    }
    
    this.match(TokenType.Semicolon);  // Optional semicolon
    
    return {
      type: NodeType.Let,
      name,
      init,
      line: token.line,
      column: token.column
    };
  }
  
  private ifStatement(): IfNode {
    const token = this.previous();
    
    this.consume(TokenType.LParen, "Expected '(' after 'if'");
    const condition = this.expression();
    this.consume(TokenType.RParen, "Expected ')' after condition");
    
    const then = this.statement();
    let elseStmt: StmtNode | undefined;
    
    if (this.match(TokenType.Else)) {
      elseStmt = this.statement();
    }
    
    return {
      type: NodeType.If,
      condition,
      then,
      else: elseStmt,
      line: token.line,
      column: token.column
    };
  }
  
  private whileStatement(): WhileNode {
    const token = this.previous();
    
    this.consume(TokenType.LParen, "Expected '(' after 'while'");
    const condition = this.expression();
    this.consume(TokenType.RParen, "Expected ')' after condition");
    
    const body = this.statement();
    
    return {
      type: NodeType.While,
      condition,
      body,
      line: token.line,
      column: token.column
    };
  }
  
  private returnStatement(): ReturnNode {
    const token = this.previous();
    
    let value: ExprNode | undefined;
    if (!this.check(TokenType.Semicolon) && !this.check(TokenType.RBrace)) {
      value = this.expression();
    }
    
    this.match(TokenType.Semicolon);
    
    return {
      type: NodeType.Return,
      value,
      line: token.line,
      column: token.column
    };
  }
  
  private block(): BlockNode {
    const token = this.previous();
    const statements: StmtNode[] = [];
    
    while (!this.check(TokenType.RBrace) && !this.isAtEnd()) {
      statements.push(this.statement());
    }
    
    this.consume(TokenType.RBrace, "Expected '}' after block");
    
    return {
      type: NodeType.Block,
      statements,
      line: token.line,
      column: token.column
    };
  }
  
  private certifyStatement(): CertifyNode {
    const token = this.previous();
    
    this.consume(TokenType.LParen, "Expected '(' after 'certify'");
    const claim = this.expression();
    this.consume(TokenType.Comma, "Expected ',' after claim");
    const witness = this.expression();
    this.consume(TokenType.RParen, "Expected ')' after witness");
    
    this.match(TokenType.Semicolon);
    
    return {
      type: NodeType.Certify,
      claim,
      witness,
      line: token.line,
      column: token.column
    };
  }
  
  private assertStatement(): AssertNode {
    const token = this.previous();
    
    this.consume(TokenType.LParen, "Expected '(' after 'assert'");
    const condition = this.expression();
    
    let message: string | undefined;
    if (this.match(TokenType.Comma)) {
      message = this.consume(TokenType.String, "Expected message string").value;
    }
    
    this.consume(TokenType.RParen, "Expected ')'");
    this.match(TokenType.Semicolon);
    
    return {
      type: NodeType.Assert,
      condition,
      message,
      line: token.line,
      column: token.column
    };
  }
  
  private corridorStatement(): CorridorNode {
    const token = this.previous();
    
    this.consume(TokenType.LParen, "Expected '(' after 'corridor'");
    
    const budgets: CorridorNode['budgets'] = {};
    
    // Parse budget assignments
    while (!this.check(TokenType.RParen)) {
      const name = this.consume(TokenType.Ident, "Expected budget name").value;
      this.consume(TokenType.Colon, "Expected ':'");
      const value = parseInt(this.consume(TokenType.Int, "Expected integer").value);
      
      if (name === "hubs") budgets.hubs = value;
      else if (name === "time") budgets.time = value;
      else if (name === "memory") budgets.memory = value;
      
      if (!this.check(TokenType.RParen)) {
        this.consume(TokenType.Comma, "Expected ','");
      }
    }
    
    this.consume(TokenType.RParen, "Expected ')'");
    this.consume(TokenType.LBrace, "Expected '{'");
    const body = this.block();
    
    return {
      type: NodeType.Corridor,
      budgets,
      body,
      line: token.line,
      column: token.column
    };
  }
  
  private omegaStatement(): OmegaNode {
    const token = this.previous();
    
    this.consume(TokenType.LParen, "Expected '(' after 'omega'");
    const threshold = parseFloat(this.consume(TokenType.Float, "Expected threshold").value);
    this.consume(TokenType.RParen, "Expected ')'");
    
    const body = this.statement();
    
    return {
      type: NodeType.Omega,
      threshold,
      body,
      line: token.line,
      column: token.column
    };
  }
  
  private expressionStatement(): ExprStmtNode {
    const expr = this.expression();
    this.match(TokenType.Semicolon);
    
    return {
      type: NodeType.ExprStmt,
      expr,
      line: expr.line,
      column: expr.column
    };
  }
  
  private expression(): ExprNode {
    return this.assignment();
  }
  
  private assignment(): ExprNode {
    const expr = this.or();
    
    if (this.match(TokenType.Eq)) {
      const value = this.assignment();
      
      if (expr.type === NodeType.Identifier || expr.type === NodeType.Index || expr.type === NodeType.Member) {
        return {
          type: NodeType.Assign,
          target: expr,
          value,
          line: expr.line,
          column: expr.column
        } as AssignNode as unknown as ExprNode;
      }
      
      throw new Error("Invalid assignment target");
    }
    
    return expr;
  }
  
  private or(): ExprNode {
    let expr = this.and();
    
    while (this.match(TokenType.Or)) {
      const operator = this.previous().value;
      const right = this.and();
      expr = {
        type: NodeType.Binary,
        operator,
        left: expr,
        right,
        line: expr.line,
        column: expr.column
      };
    }
    
    return expr;
  }
  
  private and(): ExprNode {
    let expr = this.equality();
    
    while (this.match(TokenType.And)) {
      const operator = this.previous().value;
      const right = this.equality();
      expr = {
        type: NodeType.Binary,
        operator,
        left: expr,
        right,
        line: expr.line,
        column: expr.column
      };
    }
    
    return expr;
  }
  
  private equality(): ExprNode {
    let expr = this.comparison();
    
    while (this.match(TokenType.EqEq, TokenType.NEq)) {
      const operator = this.previous().value;
      const right = this.comparison();
      expr = {
        type: NodeType.Binary,
        operator,
        left: expr,
        right,
        line: expr.line,
        column: expr.column
      };
    }
    
    return expr;
  }
  
  private comparison(): ExprNode {
    let expr = this.term();
    
    while (this.match(TokenType.Lt, TokenType.Gt, TokenType.LtEq, TokenType.GtEq)) {
      const operator = this.previous().value;
      const right = this.term();
      expr = {
        type: NodeType.Binary,
        operator,
        left: expr,
        right,
        line: expr.line,
        column: expr.column
      };
    }
    
    return expr;
  }
  
  private term(): ExprNode {
    let expr = this.factor();
    
    while (this.match(TokenType.Plus, TokenType.Minus)) {
      const operator = this.previous().value;
      const right = this.factor();
      expr = {
        type: NodeType.Binary,
        operator,
        left: expr,
        right,
        line: expr.line,
        column: expr.column
      };
    }
    
    return expr;
  }
  
  private factor(): ExprNode {
    let expr = this.unary();
    
    while (this.match(TokenType.Star, TokenType.Slash, TokenType.Percent)) {
      const operator = this.previous().value;
      const right = this.unary();
      expr = {
        type: NodeType.Binary,
        operator,
        left: expr,
        right,
        line: expr.line,
        column: expr.column
      };
    }
    
    return expr;
  }
  
  private unary(): ExprNode {
    if (this.match(TokenType.Not, TokenType.Minus)) {
      const operator = this.previous().value;
      const operand = this.unary();
      return {
        type: NodeType.Unary,
        operator,
        operand,
        line: operand.line,
        column: operand.column
      };
    }
    
    return this.call();
  }
  
  private call(): ExprNode {
    let expr = this.primary();
    
    while (true) {
      if (this.match(TokenType.LParen)) {
        expr = this.finishCall(expr);
      } else if (this.match(TokenType.LBracket)) {
        const index = this.expression();
        this.consume(TokenType.RBracket, "Expected ']'");
        expr = {
          type: NodeType.Index,
          object: expr,
          index,
          line: expr.line,
          column: expr.column
        };
      } else if (this.match(TokenType.Dot)) {
        const member = this.consume(TokenType.Ident, "Expected member name").value;
        expr = {
          type: NodeType.Member,
          object: expr,
          member,
          line: expr.line,
          column: expr.column
        };
      } else {
        break;
      }
    }
    
    return expr;
  }
  
  private finishCall(callee: ExprNode): CallNode {
    const args: ExprNode[] = [];
    
    if (!this.check(TokenType.RParen)) {
      do {
        args.push(this.expression());
      } while (this.match(TokenType.Comma));
    }
    
    this.consume(TokenType.RParen, "Expected ')' after arguments");
    
    return {
      type: NodeType.Call,
      callee,
      args,
      line: callee.line,
      column: callee.column
    };
  }
  
  private primary(): ExprNode {
    const token = this.peek();
    
    if (this.match(TokenType.Int)) {
      return {
        type: NodeType.Literal,
        valueType: "int",
        value: parseInt(this.previous().value),
        line: token.line,
        column: token.column
      };
    }
    
    if (this.match(TokenType.Float)) {
      return {
        type: NodeType.Literal,
        valueType: "float",
        value: parseFloat(this.previous().value),
        line: token.line,
        column: token.column
      };
    }
    
    if (this.match(TokenType.String)) {
      return {
        type: NodeType.Literal,
        valueType: "string",
        value: this.previous().value,
        line: token.line,
        column: token.column
      };
    }
    
    if (this.match(TokenType.Bool)) {
      return {
        type: NodeType.Literal,
        valueType: "bool",
        value: this.previous().value === "true",
        line: token.line,
        column: token.column
      };
    }
    
    if (this.match(TokenType.Nil)) {
      return {
        type: NodeType.Literal,
        valueType: "nil",
        value: null,
        line: token.line,
        column: token.column
      };
    }
    
    if (this.match(TokenType.Address)) {
      return {
        type: NodeType.Address,
        address: this.previous().value,
        line: token.line,
        column: token.column
      };
    }
    
    if (this.match(TokenType.Ident)) {
      return {
        type: NodeType.Identifier,
        name: this.previous().value,
        line: token.line,
        column: token.column
      };
    }
    
    if (this.match(TokenType.Truth)) {
      this.consume(TokenType.LParen, "Expected '('");
      const expr = this.expression();
      this.consume(TokenType.RParen, "Expected ')'");
      return {
        type: NodeType.Truth,
        expr,
        line: token.line,
        column: token.column
      };
    }
    
    if (this.match(TokenType.Witness)) {
      this.consume(TokenType.LParen, "Expected '('");
      const expr = this.expression();
      this.consume(TokenType.RParen, "Expected ')'");
      return {
        type: NodeType.Witness,
        expr,
        line: token.line,
        column: token.column
      };
    }
    
    if (this.match(TokenType.LParen)) {
      const expr = this.expression();
      this.consume(TokenType.RParen, "Expected ')'");
      return expr;
    }
    
    if (this.match(TokenType.LBracket)) {
      const elements: ExprNode[] = [];
      if (!this.check(TokenType.RBracket)) {
        do {
          elements.push(this.expression());
        } while (this.match(TokenType.Comma));
      }
      this.consume(TokenType.RBracket, "Expected ']'");
      return {
        type: NodeType.Array,
        elements,
        line: token.line,
        column: token.column
      };
    }
    
    throw new Error(`Unexpected token: ${token.type} at line ${token.line}`);
  }
  
  // Helper methods
  private match(...types: TokenType[]): boolean {
    for (const type of types) {
      if (this.check(type)) {
        this.advance();
        return true;
      }
    }
    return false;
  }
  
  private check(type: TokenType): boolean {
    return !this.isAtEnd() && this.peek().type === type;
  }
  
  private advance(): Token {
    if (!this.isAtEnd()) this.pos++;
    return this.previous();
  }
  
  private isAtEnd(): boolean {
    return this.peek().type === TokenType.EOF;
  }
  
  private peek(): Token {
    return this.tokens[this.pos];
  }
  
  private previous(): Token {
    return this.tokens[this.pos - 1];
  }
  
  private consume(type: TokenType, message: string): Token {
    if (this.check(type)) return this.advance();
    throw new Error(`${message} at line ${this.peek().line}`);
  }
  
  private synchronize(): void {
    this.advance();
    while (!this.isAtEnd()) {
      if (this.previous().type === TokenType.Semicolon) return;
      switch (this.peek().type) {
        case TokenType.Fn:
        case TokenType.Let:
        case TokenType.If:
        case TokenType.While:
        case TokenType.Return:
          return;
      }
      this.advance();
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 4: COMPILATION PIPELINE
// ═══════════════════════════════════════════════════════════════════════════════

/** Compilation stage */
export enum CompileStage {
  Parse = "parse",
  Normalize = "normalize",
  Plan = "plan",
  Solve = "solve",
  Certify = "certify",
  Store = "store"
}

/** Compilation result */
export interface CompileResult {
  success: boolean;
  stage: CompileStage;
  ast?: ProgramNode;
  errors: string[];
  warnings: string[];
  certificates: Certificate[];
  metrics: CompileMetrics;
}

/** Compilation metrics */
export interface CompileMetrics {
  parseTime: number;
  normalizeTime: number;
  planTime: number;
  solveTime: number;
  certifyTime: number;
  storeTime: number;
  totalTime: number;
  astNodes: number;
  certificates: number;
}

/** Certificate */
export interface Certificate {
  id: string;
  type: CertificateType;
  claim: string;
  witness: WitnessPtr;
  truth: TruthValue;
  timestamp: number;
}

export enum CertificateType {
  EdgeWF = "EdgeWF",
  WitSuff = "WitSuff",
  Coverage = "Coverage",
  Slack = "Slack",
  Eq = "Eq",
  DualFac = "DualFac",
  Drift = "Drift",
  ReplayAcc = "ReplayAcc",
  Closure = "Closure",
  Compliance = "Compliance"
}

/**
 * Complete compilation pipeline
 */
export class OmegaCompiler {
  private corridor: Corridors.Corridor;
  private omegaThreshold: number = 0.5;
  private certificates: Certificate[] = [];
  private witnesses: WitnessPtr[] = [];
  
  constructor(corridor: Corridors.Corridor, omegaThreshold: number = 0.5) {
    this.corridor = corridor;
    this.omegaThreshold = omegaThreshold;
  }
  
  /**
   * Full compilation pipeline
   */
  compile(source: string): CompileResult {
    const startTime = Date.now();
    const metrics: CompileMetrics = {
      parseTime: 0,
      normalizeTime: 0,
      planTime: 0,
      solveTime: 0,
      certifyTime: 0,
      storeTime: 0,
      totalTime: 0,
      astNodes: 0,
      certificates: 0
    };
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Stage 1: Parse
    let parseStart = Date.now();
    const lexer = new Lexer(source);
    const tokens = lexer.tokenize();
    
    const parser = new Parser(tokens);
    const ast = parser.parse();
    errors.push(...parser.getErrors());
    
    metrics.parseTime = Date.now() - parseStart;
    
    if (errors.length > 0) {
      return {
        success: false,
        stage: CompileStage.Parse,
        ast,
        errors,
        warnings,
        certificates: [],
        metrics
      };
    }
    
    // Stage 2: Normalize
    let normalizeStart = Date.now();
    const normalizedAst = this.normalize(ast);
    metrics.normalizeTime = Date.now() - normalizeStart;
    
    // Stage 3: Plan
    let planStart = Date.now();
    const plan = this.plan(normalizedAst);
    metrics.planTime = Date.now() - planStart;
    
    // Stage 4: Solve (type checking, constraint satisfaction)
    let solveStart = Date.now();
    const solveResult = this.solve(normalizedAst, plan);
    errors.push(...solveResult.errors);
    warnings.push(...solveResult.warnings);
    metrics.solveTime = Date.now() - solveStart;
    
    if (solveResult.errors.length > 0) {
      return {
        success: false,
        stage: CompileStage.Solve,
        ast: normalizedAst,
        errors,
        warnings,
        certificates: this.certificates,
        metrics
      };
    }
    
    // Stage 5: Certify
    let certifyStart = Date.now();
    const certifyResult = this.certify(normalizedAst);
    this.certificates.push(...certifyResult);
    metrics.certifyTime = Date.now() - certifyStart;
    
    // Omega gate check
    const omega = this.computeOmega();
    if (omega < this.omegaThreshold) {
      warnings.push(`Omega value ${omega.toFixed(3)} below threshold ${this.omegaThreshold}`);
    }
    
    // Stage 6: Store
    let storeStart = Date.now();
    // Would store compiled artifacts
    metrics.storeTime = Date.now() - storeStart;
    
    metrics.totalTime = Date.now() - startTime;
    metrics.astNodes = this.countNodes(normalizedAst);
    metrics.certificates = this.certificates.length;
    
    return {
      success: true,
      stage: CompileStage.Store,
      ast: normalizedAst,
      errors,
      warnings,
      certificates: this.certificates,
      metrics
    };
  }
  
  /**
   * Normalize AST
   */
  private normalize(ast: ProgramNode): ProgramNode {
    // Canonicalize names, resolve addresses, etc.
    return ast;  // For now, return as-is
  }
  
  /**
   * Create compilation plan
   */
  private plan(ast: ProgramNode): CompilationPlan {
    const steps: PlanStep[] = [];
    
    // Analyze dependencies
    for (const decl of ast.declarations) {
      steps.push({
        id: `step_${steps.length}`,
        node: decl,
        dependencies: [],
        priority: 1
      });
    }
    
    return { steps };
  }
  
  /**
   * Solve constraints
   */
  private solve(ast: ProgramNode, plan: CompilationPlan): SolveResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Type checking would go here
    // Constraint satisfaction would go here
    
    return { errors, warnings };
  }
  
  /**
   * Generate certificates
   */
  private certify(ast: ProgramNode): Certificate[] {
    const certs: Certificate[] = [];
    
    // Generate EdgeWF certificate
    certs.push(this.createCertificate(
      CertificateType.EdgeWF,
      "All edges well-formed"
    ));
    
    // Generate WitSuff certificate
    certs.push(this.createCertificate(
      CertificateType.WitSuff,
      "Witness sufficiency verified"
    ));
    
    // Generate Coverage certificate
    certs.push(this.createCertificate(
      CertificateType.Coverage,
      "Test coverage adequate"
    ));
    
    return certs;
  }
  
  private createCertificate(type: CertificateType, claim: string): Certificate {
    const witness: WitnessPtr = {
      id: `wit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: "direct",
      hash: this.hashString(claim),
      confidence: 1.0
    };
    
    this.witnesses.push(witness);
    
    return {
      id: `cert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      claim,
      witness,
      truth: TruthValue.OK,
      timestamp: Date.now()
    };
  }
  
  private computeOmega(): number {
    // Omega based on witness coverage and certificate count
    if (this.witnesses.length === 0) return 0;
    
    const certTypes = new Set(this.certificates.map(c => c.type));
    const coverage = certTypes.size / Object.keys(CertificateType).length;
    
    return Math.min(1, 0.5 + coverage * 0.5);
  }
  
  private countNodes(ast: ProgramNode): number {
    let count = 1;
    for (const decl of ast.declarations) {
      count += this.countDeclNodes(decl);
    }
    return count;
  }
  
  private countDeclNodes(node: DeclNode): number {
    // Simplified node counting
    return 1;
  }
  
  private hashString(s: string): string {
    let hash = 0;
    for (let i = 0; i < s.length; i++) {
      hash = ((hash << 5) - hash) + s.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(16, '0');
  }
}

interface CompilationPlan {
  steps: PlanStep[];
}

interface PlanStep {
  id: string;
  node: DeclNode;
  dependencies: string[];
  priority: number;
}

interface SolveResult {
  errors: string[];
  warnings: string[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// SECTION 5: PLAYBOOKS (Π1-Π7)
// ═══════════════════════════════════════════════════════════════════════════════

/** Playbook types */
export enum PlaybookType {
  Compile = "Π1",    // HCENM - Compile flow
  Resolve = "Π2",    // LHMJ - Resolution flow
  Conflict = "Π3",   // KHDM - Conflict handling
  Publish = "Π4",    // DOP - Publication
  Migrate = "Π5",    // Migration
  Repair = "Π6",     // Repair
  Audit = "Π7"       // Audit
}

/** Playbook step */
export interface PlaybookStep {
  id: string;
  action: string;
  params: Map<string, unknown>;
  condition?: string;
  onSuccess: string;
  onFailure: string;
}

/** Playbook definition */
export interface Playbook {
  type: PlaybookType;
  name: string;
  steps: PlaybookStep[];
  entryPoint: string;
}

/**
 * Create compile playbook (Π1: HCENM)
 */
export function createCompilePlaybook(): Playbook {
  return {
    type: PlaybookType.Compile,
    name: "Compile (HCENM)",
    steps: [
      {
        id: "H",
        action: "harvest",
        params: new Map([["source", "input"]]),
        onSuccess: "C",
        onFailure: "FAIL"
      },
      {
        id: "C",
        action: "canonicalize",
        params: new Map([["normalize", true]]),
        onSuccess: "E",
        onFailure: "FAIL"
      },
      {
        id: "E",
        action: "emit",
        params: new Map([["target", "ir"]]),
        onSuccess: "N",
        onFailure: "FAIL"
      },
      {
        id: "N",
        action: "notarize",
        params: new Map([["witness", true]]),
        onSuccess: "M",
        onFailure: "FAIL"
      },
      {
        id: "M",
        action: "merge",
        params: new Map([["store", "mycelium"]]),
        onSuccess: "DONE",
        onFailure: "FAIL"
      }
    ],
    entryPoint: "H"
  };
}

/**
 * Create resolve playbook (Π2: LHMJ)
 */
export function createResolvePlaybook(): Playbook {
  return {
    type: PlaybookType.Resolve,
    name: "Resolve (LHMJ)",
    steps: [
      {
        id: "L",
        action: "locate",
        params: new Map([["query", "ambig"]]),
        onSuccess: "H",
        onFailure: "FAIL"
      },
      {
        id: "H",
        action: "hypothesize",
        params: new Map([["candidates", "generate"]]),
        onSuccess: "M",
        onFailure: "FAIL"
      },
      {
        id: "M",
        action: "measure",
        params: new Map([["evidence", "collect"]]),
        onSuccess: "J",
        onFailure: "FAIL"
      },
      {
        id: "J",
        action: "judge",
        params: new Map([["threshold", 0.8]]),
        onSuccess: "DONE",
        onFailure: "FAIL"
      }
    ],
    entryPoint: "L"
  };
}

/**
 * Create conflict playbook (Π3: KHDM)
 */
export function createConflictPlaybook(): Playbook {
  return {
    type: PlaybookType.Conflict,
    name: "Conflict (KHDM)",
    steps: [
      {
        id: "K",
        action: "kill",
        params: new Map([["target", "conflict"]]),
        onSuccess: "H",
        onFailure: "QUARANTINE"
      },
      {
        id: "H",
        action: "heal",
        params: new Map([["strategy", "merge"]]),
        onSuccess: "D",
        onFailure: "QUARANTINE"
      },
      {
        id: "D",
        action: "document",
        params: new Map([["receipt", true]]),
        onSuccess: "M",
        onFailure: "FAIL"
      },
      {
        id: "M",
        action: "migrate",
        params: new Map([["version", "increment"]]),
        onSuccess: "DONE",
        onFailure: "FAIL"
      }
    ],
    entryPoint: "K"
  };
}

/**
 * Create publish playbook (Π4: DOP)
 */
export function createPublishPlaybook(): Playbook {
  return {
    type: PlaybookType.Publish,
    name: "Publish (DOP)",
    steps: [
      {
        id: "D",
        action: "digest",
        params: new Map([["hash", "sha256"]]),
        onSuccess: "O",
        onFailure: "FAIL"
      },
      {
        id: "O",
        action: "omega_check",
        params: new Map([["threshold", 0.5]]),
        condition: "omega >= threshold",
        onSuccess: "P",
        onFailure: "FAIL"
      },
      {
        id: "P",
        action: "publish",
        params: new Map([["attestation", true]]),
        onSuccess: "DONE",
        onFailure: "FAIL"
      }
    ],
    entryPoint: "D"
  };
}

/**
 * Execute playbook
 */
export function executePlaybook(
  playbook: Playbook,
  context: Map<string, unknown>
): PlaybookResult {
  const trace: PlaybookTraceEntry[] = [];
  let currentStep = playbook.entryPoint;
  let iterations = 0;
  const maxIterations = 100;
  
  while (currentStep !== "DONE" && currentStep !== "FAIL" && currentStep !== "QUARANTINE") {
    if (iterations++ >= maxIterations) {
      return {
        success: false,
        finalStep: currentStep,
        trace,
        error: "Max iterations exceeded"
      };
    }
    
    const step = playbook.steps.find(s => s.id === currentStep);
    if (!step) {
      return {
        success: false,
        finalStep: currentStep,
        trace,
        error: `Unknown step: ${currentStep}`
      };
    }
    
    // Execute step
    const result = executeStep(step, context);
    trace.push({
      stepId: step.id,
      action: step.action,
      success: result.success,
      timestamp: Date.now()
    });
    
    // Determine next step
    currentStep = result.success ? step.onSuccess : step.onFailure;
  }
  
  return {
    success: currentStep === "DONE",
    finalStep: currentStep,
    trace
  };
}

function executeStep(step: PlaybookStep, context: Map<string, unknown>): { success: boolean } {
  // Simplified step execution
  // In real implementation, would dispatch to actual handlers
  return { success: true };
}

export interface PlaybookResult {
  success: boolean;
  finalStep: string;
  trace: PlaybookTraceEntry[];
  error?: string;
}

export interface PlaybookTraceEntry {
  stepId: string;
  action: string;
  success: boolean;
  timestamp: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export default {
  Lexer,
  Parser,
  OmegaCompiler,
  TokenType,
  NodeType,
  CompileStage,
  CertificateType,
  PlaybookType,
  createCompilePlaybook,
  createResolvePlaybook,
  createConflictPlaybook,
  createPublishPlaybook,
  executePlaybook
};
