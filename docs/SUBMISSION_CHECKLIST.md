# Submission checklist

Checked against the sprint page on 9 November 2026. Re-read the Guidelines tab
on the day; the page says to always use the template linked there.

Deadline: Sunday 15 Nov 2026, 11:59 PM Anywhere on Earth
= **Monday 16 Nov, 12:59 PM Lagos time**. Target: Sunday 9 PM Lagos.

## The report (PDF, max 25 MB)

Template read on 11 Nov 2026 (text export of the official Google Doc). Open
your own copy for the exact wording; this is its structure:

- [ ] Title, author names and affiliations, footnote naming the sprint
- [ ] Abstract, 150 to 250 words (write it last)
- [ ] 1. Introduction: problem, why it matters, threat model, contributions
- [ ] 2. Related Work: closest work, how this differs, the gap
- [ ] 3. Methods: enough to replicate; design choices; what did not work
- [ ] 4. Results: at least one numbered figure or table; observations kept
      apart from interpretation; robustness
- [ ] 5. Discussion and Limitations: implications, limits, future work
- [ ] 6. Conclusion: one or two paragraphs
- [ ] Code and Data: repository link, any info-hazard note
- [ ] Author Contributions (optional)
- [ ] References with URLs or DOIs, every one opened and read
- [ ] Appendix (optional)
- [ ] LLM Usage Statement: how AI help was used, and that the team verified
      every claim and is responsible for the final text

Length: the template suggests about 4 pages before references and appendix
(about 1 intro and related work, 2.5 methods and results, 0.5 discussion).
The sprint page caps it at 8. Aim for 4 to 5.

Also required by the sprint page:

- [ ] Limitations and dual-use / ethics covered: what the result does and
      does not establish; how it could be misused; personal data (none is
      used: the workload is synthetic)
- [ ] Pre-sprint work stated in the report, matching `PRE_SPRINT.md`
- [ ] Every number traces to a file in `results/`
- [ ] All links work
- [ ] Read start to finish, and edited, by the author

## The form (on the sprint page, "Submit your project")

Required:

- [ ] Project title (keep it identical if you resubmit)
- [ ] Project summary (short abstract: what you did, what you found)
- [ ] PDF report
- [ ] Interested in publishing? Yes / No
- [ ] Team name
- [ ] Location
- [ ] Team member 1: name and email

Optional:

- [ ] Tracks: tick "Track 2: Trust Infrastructure"
- [ ] Project code: public repository link
- [ ] Presentation recording (3 to 5 minute video)
- [ ] Slides (PDF, PowerPoint, Keynote or ODP, max 25 MB)
- [ ] Project image (PNG, JPEG, WebP or GIF, max 25 MB)
- [ ] Additional material
- [ ] Discord username, Google Scholar profile

## After pressing submit

- [ ] Confirmation email arrived with the right title and the right PDF
      (check spam; if nothing, email sprints@apartresearch.com)
- [ ] To fix anything: submit again with the **same title** before the
      deadline. Do not email the PDF.
- [ ] The project will not appear on the website until after judging.

## Repository

- [ ] README marks pre-sprint code as pre-existing
- [ ] `requirements.lock` matches the versions in the report
- [ ] `python -m pytest -q` passes on a fresh clone
- [ ] No tool-specific exploit detail public while a maintainer note is open
