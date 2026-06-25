# Website Side Hustle Guide

This guide is for people who want to publish or use this repository as a practical starter kit for small-business website work.

The core idea: a useful AI website side-hustle is not just "make a pretty homepage." It is a repeatable delivery system that helps a beginner collect client facts, build an original website, set up a simple inquiry or reservation workflow, test the result, and hand it to a real business with clear human approval boundaries.

If you want to use Codex, Claude Code, Cursor, or another coding agent, also read [Website Project Agent Guide](WEBSITE_PROJECT_AGENT_GUIDE.md).

## What this should become

Not "an AI that can make pretty sites."

Instead:

- a safe client brief process
- commercial-use-aware public source research
- originality and license rules
- a repeatable AI workflow for design and implementation
- reservation and inquiry aggregation for the back office
- browser QA and delivery checklists
- proposal, pricing, and maintenance documents

That is what makes the pack useful for real side-hustle work.

## Who this is for

This project is useful for:

- beginners who want a structured first website service
- Codex, Claude Code, and Cursor users who want a repeatable workflow
- freelancers who need client-facing checklists and proposal assets
- small agencies that want safer AI-assisted delivery
- local businesses that need a simple website plus inquiry handling

This project is not for:

- copying competitor websites
- bypassing designers on high-stakes brand projects
- guaranteeing SEO rankings, leads, or bookings
- automating real reservations, payments, or customer replies without review

## Public resources worth including

Use public sources as ingredients, not as permission to clone.

- `shadcn/ui`: accessible UI primitives for React websites
- `Astro`: fast static-site framework for brochure and content-heavy sites
- `Headless UI`: accessible menus, dialogs, and disclosures
- `Open Props`: CSS tokens for spacing, typography, and motion
- `lucide`: icon set for navigation and feature cards
- WCAG quick reference: accessibility baseline
- `web.dev/accessibility`: practical implementation guidance
- Google Search SEO starter guide: on-page SEO basics
- `schema.org/Hotel` and related schema types: structured data references

## Offer design

The strongest entry offer is usually not "I can build any website."

Start narrower:

- tourism hotel or villa homepage
- clinic or therapist website
- salon or beauty studio site
- restaurant or cafe homepage
- lawyer, accountant, or consultant brochure site
- local trades landing page

Each niche needs different proof, CTA, policy language, and trust signals.

## Quality bar

A side-hustle website pack becomes valuable when it helps a beginner avoid four common failures:

1. Copying a competitor too closely
2. Shipping a pretty page with weak CTA and no trust content
3. Forgetting mobile QA and accessibility
4. Finishing the code but having no proposal, price menu, maintenance scope, or inquiry operations process

## Practical workflow

1. Pick one niche
2. Gather facts with a client brief
3. Choose public references and record their licenses
4. Create an original direction, not a direct clone
5. Build the page
6. Create the reservation or inquiry intake table, status pipeline, and response templates
7. Check desktop, mobile, forms, and the back-office dashboard in a real browser
8. Deliver with a handoff and maintenance option

## Front website workflow

For the public website, work in this order:

1. Define the visitor: tourist, patient, local customer, business owner, repeat customer, or first-time buyer.
2. Define the main action: book, inquire, call, request a quote, visit, or reserve.
3. Collect proof: real photos, reviews, credentials, years in business, staff information, or local details.
4. Create a simple section order: hero, reasons to choose, services or rooms, process, proof, access, FAQ, final CTA.
5. Build the page with responsive layout and accessible labels.
6. Check the site in a real browser on desktop and mobile.

Good website output should answer three questions quickly:

- What is this business?
- Why should I trust it?
- What should I do next?

## Back-office workflow

The back-office layer makes the package more useful than a static brochure.

Start with one intake table. Every website form, email, phone note, LINE message, booking portal export, or manual staff note should become one row.

Use these basic fields:

- lead ID
- received time
- source
- customer name
- contact method
- requested date, service, room, or plan
- message
- status
- priority
- owner
- next action due
- consent or privacy note

Use these statuses:

- `new`
- `needs-info`
- `availability-check`
- `quoted`
- `tentative`
- `confirmed`
- `declined`
- `canceled`
- `follow-up`

Keep the first version simple. Google Forms plus Google Sheets is often enough for a beginner pilot. Airtable, Notion, Zapier, Make, n8n, or a custom backend can come later after the manual process is stable.

## Daily operator routine

The operator should check the inquiry table every business day:

1. Review new rows.
2. Remove spam and duplicates.
3. Mark missing information.
4. Ask the business owner or staff to check availability, prices, and exceptions.
5. Draft a reply.
6. Get human approval.
7. Send the reply.
8. Update the status and next action due date.

This daily routine is part of the product. It tells the client how the website turns into real customer handling.

## What to automate, what to keep human

Good AI-assisted tasks:

- structure ideas
- component implementation
- copy drafting from approved facts
- inquiry classification and reply drafting
- page QA checklists
- proposal scaffolding

Keep human approval for:

- legal and license judgment
- final brand tone
- real client facts
- reservation confirmation, price exceptions, and policy exceptions
- launch approval
- pricing commitments

Never automate:

- final booking confirmation
- payment collection through an unreviewed form
- price exceptions
- cancellation or refund exceptions
- legal, privacy, or license judgments
- production email, SMS, LINE, or CRM sending without approval

## Use the generated pack

Run:

```bash
ai-automation-kit website-side-hustle --industry hospitality --client-type local-business --niche tourism-hotel --output .tmp/website-side-hustle
```

That output gives you a commercial-use-aware source catalog, client brief, Codex workflow, reservation and inquiry operations templates, proposal, pricing, maintenance, QA, launch checklist, a small editable sample site, and a static back-office dashboard mockup.

Important generated files for beginners:

- `ai_agent_handoff.md`: copy-ready instruction for Codex, Claude Code, Cursor, or another agent
- `beginner_human_guide.md`: plain English guide for the human operator
- `beginner_human_guide.ja.md`: plain Japanese guide for the human operator
- `reservation_inquiry_system.md`: back-office system overview
- `inquiry_dashboard.html`: browser-friendly back-office mockup

## Suggested first paid offer

Start with a narrow offer:

> I will create a mobile-friendly homepage and a simple inquiry management setup for your business, including a contact path, inquiry table, response templates, and a handoff guide.

Keep the first scope small:

- one homepage or brochure page
- one contact or booking path
- one inquiry table
- one status pipeline
- five response templates
- one browser check on desktop and mobile
- one handoff session or handoff note

This is easier to sell, easier to deliver, and safer than promising a full custom system.
