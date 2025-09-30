/**
 * Sanitization utilities tests
 */

import { describe, it, expect } from 'vitest';
import { sanitizeHTML, sanitizeText, escapeHTML } from '../utils/sanitize';

describe('sanitizeHTML', () => {
  it('should remove script tags', () => {
    const dirty = '<script>alert("XSS")</script><p>Hello</p>';
    const clean = sanitizeHTML(dirty);
    expect(clean).not.toContain('<script>');
    expect(clean).toContain('<p>Hello</p>');
  });

  it('should allow safe tags', () => {
    const html = '<p>Hello <b>World</b></p>';
    const clean = sanitizeHTML(html);
    expect(clean).toContain('<p>');
    expect(clean).toContain('<b>');
  });

  it('should remove event handlers', () => {
    const dirty = '<p onclick="alert(\'XSS\')">Hello</p>';
    const clean = sanitizeHTML(dirty);
    expect(clean).not.toContain('onclick');
  });
});

describe('sanitizeText', () => {
  it('should remove all HTML tags', () => {
    const dirty = '<script>alert("XSS")</script>Hello';
    const clean = sanitizeText(dirty);
    expect(clean).not.toContain('<script>');
    expect(clean).toContain('Hello');
  });

  it('should keep text content', () => {
    const text = 'Plain text content';
    const clean = sanitizeText(text);
    expect(clean).toBe(text);
  });
});

describe('escapeHTML', () => {
  it('should escape HTML entities', () => {
    const text = '<div>Test & "quotes"</div>';
    const escaped = escapeHTML(text);
    expect(escaped).toContain('&lt;');
    expect(escaped).toContain('&gt;');
  });

  it('should handle plain text', () => {
    const text = 'Plain text';
    const escaped = escapeHTML(text);
    expect(escaped).toBe(text);
  });
});