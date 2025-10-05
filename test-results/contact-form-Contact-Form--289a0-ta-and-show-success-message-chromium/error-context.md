# Page snapshot

```yaml
- generic [ref=e2]:
  - heading "Get in Touch" [level=1] [ref=e3]
  - paragraph [ref=e4]: Fill out the form below and we'll get back to you as soon as possible.
  - generic [ref=e5]:
    - generic [ref=e6]:
      - generic [ref=e7]:
        - text: Full Name
        - generic [ref=e8]: "*"
      - textbox "Full Name *" [ref=e9]: John Doe
      - generic [ref=e10]:
        - generic [ref=e11]: "8"
        - text: /100
    - generic [ref=e12]:
      - generic [ref=e13]:
        - text: Email Address
        - generic [ref=e14]: "*"
      - textbox "Email Address *" [ref=e15]: john@example.com
      - generic [ref=e16]:
        - generic [ref=e17]: "16"
        - text: /254
    - button "Send Message" [ref=e18] [cursor=pointer]
    - status [ref=e19]: Submission failed. Please try again.
```