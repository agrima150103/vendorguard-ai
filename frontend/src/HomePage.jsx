import { useEffect, useState } from "react";

import "./homepage.css";


const NAV_LINKS = [
  {
    href: "#how-it-works",
    label: "How it works",
    sectionId: "how-it-works",
  },
  {
    href: "#architecture",
    label: "Architecture",
    sectionId: "architecture",
  },
  {
    href: "#security",
    label: "Security",
    sectionId: "security",
  },
  {
    href: "#vendors",
    label: "Try a vendor",
    sectionId: "vendors",
  },
];


const PIPELINE_STEPS = [
  {
    step: "01",
    title: "Evidence Agent",
    text:
      "Extracts source-backed claims from every vendor document and preserves the original source and location.",
    accent: "purple",
  },
  {
    step: "02",
    title: "Risk & Security Agent",
    text:
      "Detects prompt-injection attempts, contradictions, missing evidence, and material security risks.",
    accent: "amber",
  },
  {
    step: "03",
    title: "Policy Agent (MCP)",
    text:
      "Checks evidence against governed onboarding policies through a dedicated MCP tool boundary.",
    accent: "green",
  },
  {
    step: "04",
    title: "Decision Agent",
    text:
      "Combines evidence, risk findings, and policy results into a structured, non-binding recommendation.",
    accent: "blue",
  },
  {
    step: "05",
    title: "Human Review",
    text:
      "A reviewer records the final outcome, rationale, and any conditions before the assessment is complete.",
    accent: "pink",
  },
];


const ARCHITECTURE_LAYERS = [
  {
    label: "React frontend",
    detail:
      "Vendor selection, assessment views, evidence ledger, audit trail, and human-review interface.",
  },
  {
    label: "FastAPI backend",
    detail:
      "API endpoints, orchestration, validation, persistence, and review handling.",
  },
  {
    label: "ADK SequentialAgent",
    detail:
      "Evidence → Risk & Security → Policy → Decision.",
  },
  {
    label: "MCP policy server",
    detail:
      "Governed onboarding rules delivered through an isolated policy tool boundary.",
  },
  {
    label: "Human approval gate",
    detail:
      "The only stage where a recommendation becomes a recorded final decision.",
  },
  {
    label: "SQLite audit store",
    detail:
      "Assessment records, findings, recommendations, and human decisions.",
  },
];


const SECURITY_POINTS = [
  {
    title: "Untrusted-content boundary",
    text:
      "Vendor-controlled documents are analysed as evidence and are never treated as executable instructions.",
  },
  {
    title: "Tool allowlisting",
    text:
      "Each agent receives only the tools required for its specific assessment responsibility.",
  },
  {
    title: "Mandatory human approval",
    text:
      "Every recommendation remains non-binding until a reviewer records the final outcome.",
  },
  {
    title: "Auditable fallback",
    text:
      "If the external model is unavailable, deterministic controls complete the assessment and record the mode used.",
  },
];


const WORKFLOW_STAGES = [
  {
    number: "01",
    title: "Evidence extraction",
    detail: "Source-backed claims",
    accent: "purple",
  },
  {
    number: "02",
    title: "Risk analysis",
    detail: "Security findings",
    accent: "amber",
  },
  {
    number: "03",
    title: "Policy checks",
    detail: "Governed through MCP",
    accent: "green",
  },
  {
    number: "04",
    title: "Recommendation",
    detail: "Non-binding outcome",
    accent: "blue",
  },
  {
    number: "05",
    title: "Human review",
    detail: "Final decision gate",
    accent: "pink",
  },
];


function getInitialTheme() {
  const savedTheme = localStorage.getItem(
    "vendorguard-theme",
  );

  if (
    savedTheme === "dark" ||
    savedTheme === "light"
  ) {
    return savedTheme;
  }

  return "dark";
}


export default function HomePage({
  vendors,
  loading,
  startingVendorId,
  onSelect,
  onOpenHistory,
}) {
  const [theme, setTheme] = useState(
    getInitialTheme,
  );

  const [activeSection, setActiveSection] =
    useState("");

  useEffect(() => {
    localStorage.setItem(
      "vendorguard-theme",
      theme,
    );
  }, [theme]);

  useEffect(() => {
    const sectionElements = NAV_LINKS.map(
      (link) =>
        document.getElementById(
          link.sectionId,
        ),
    ).filter(Boolean);

    if (sectionElements.length === 0) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries
          .filter(
            (entry) => entry.isIntersecting,
          )
          .sort(
            (first, second) =>
              second.intersectionRatio -
              first.intersectionRatio,
          )[0];

        if (visibleEntry) {
          setActiveSection(
            visibleEntry.target.id,
          );
        }
      },
      {
        rootMargin: "-25% 0px -55% 0px",
        threshold: [0.1, 0.25, 0.5],
      },
    );

    sectionElements.forEach((section) => {
      observer.observe(section);
    });

    return () => {
      observer.disconnect();
    };
  }, []);

  function toggleTheme() {
    setTheme((currentTheme) =>
      currentTheme === "dark"
        ? "light"
        : "dark",
    );
  }

  return (
    <div
      className="vg-home-page"
      data-theme={theme}
    >
      <SiteNav
        theme={theme}
        activeSection={activeSection}
        onToggleTheme={toggleTheme}
        onOpenHistory={onOpenHistory}
      />

      <Hero />

      <PipelineSection />

      <ArchitectureSection />

      <SecuritySection />

      <VendorSection
        vendors={vendors}
        loading={loading}
        startingVendorId={
          startingVendorId
        }
        onSelect={onSelect}
      />

      <SiteFooter />
    </div>
  );
}


function SiteNav({
  theme,
  activeSection,
  onToggleTheme,
  onOpenHistory,
}) {
  return (
    <header className="vg-nav">
      <div className="vg-nav-inner">
        <a
          href="#top"
          className="vg-nav-logo"
          aria-label="VendorGuard AI home"
        >
          <span
            className="vg-nav-logo-mark"
            aria-hidden="true"
          />

          <span>VendorGuard</span>

          <span className="vg-brand-ai">
            AI
          </span>
        </a>

        <nav
          className="vg-nav-links"
          aria-label="Homepage navigation"
        >
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={
                activeSection ===
                link.sectionId
                  ? "vg-nav-link vg-nav-link-active"
                  : "vg-nav-link"
              }
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="vg-nav-actions">
          <button
            type="button"
            className="vg-nav-cta"
            onClick={onOpenHistory}
          >
            Assessments
          </button>

          <button
            type="button"
            className="vg-theme-toggle"
            onClick={onToggleTheme}
            aria-label={`Switch to ${
              theme === "dark"
                ? "light"
                : "dark"
            } theme`}
          >
            <span aria-hidden="true">
              {theme === "dark"
                ? "☀"
                : "☾"}
            </span>

            <span className="vg-theme-toggle-text">
              {theme === "dark"
                ? "Light"
                : "Dark"}
            </span>
          </button>

          <a
            href="https://github.com/agrima150103/vendorguard-ai"
            target="_blank"
            rel="noreferrer"
            className="vg-nav-cta"
          >
            View source
          </a>
        </div>
      </div>
    </header>
  );
}


function Hero() {
  return (
    <main
      id="top"
      className="vg-hero"
    >
      <div className="vg-hero-copy">
        <p className="vg-eyebrow">
          Kaggle AI Agents Capstone ·
          Agents for Business
        </p>

        <h1 className="vg-hero-title">
          <span>VendorGuard</span>
          <span className="vg-hero-ai">
            AI
          </span>
        </h1>

        <p className="vg-hero-description">
          Evidence-backed vendor
          assessment with prompt-injection
          defence, governed policy checks,
          and a mandatory human decision.
          Agents can recommend an outcome,
          but only a human reviewer can
          record the final decision.
        </p>

        <div className="vg-hero-actions">
          <a
            href="#vendors"
            className="vg-btn-primary"
          >
            Run a live assessment
          </a>

          <a
            href="#how-it-works"
            className="vg-btn-secondary"
          >
            See how the agents work
          </a>
        </div>

        <div className="vg-hero-principle">
          Every finding has evidence.
          Every action has permission.
          Every decision has a trace.
        </div>
      </div>

      <div className="vg-hero-visual">
        <div className="vg-visual-glow" />

        <div className="vg-live-card">
          <div className="vg-live-card-header">
            <div>
              <span className="vg-live-label">
                Live workflow
              </span>

              <h2>
                Assessment pipeline
              </h2>
            </div>

            <span className="vg-live-status">
              Operational
            </span>
          </div>

          <div className="vg-agent-flow">
            {WORKFLOW_STAGES.map(
              (stage, index) => (
                <div
                  className={`vg-agent-flow-row vg-accent-${stage.accent}`}
                  key={stage.number}
                >
                  <div className="vg-agent-flow-icon">
                    {stage.number}
                  </div>

                  <div className="vg-agent-flow-content">
                    <strong>
                      {stage.title}
                    </strong>

                    <span>
                      {stage.detail}
                    </span>
                  </div>

                  <span className="vg-agent-flow-state" />

                  {index <
                    WORKFLOW_STAGES.length -
                      1 && (
                    <span className="vg-agent-connector" />
                  )}
                </div>
              ),
            )}
          </div>

          <div className="vg-live-summary">
            <div>
              <span>
                Evidence traceability
              </span>
              <strong>Enabled</strong>
            </div>

            <div>
              <span>
                Human approval
              </span>
              <strong>Required</strong>
            </div>

            <div>
              <span>
                Fallback controls
              </span>
              <strong>Available</strong>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}


function PipelineSection() {
  return (
    <section
      id="how-it-works"
      className="vg-section"
    >
      <div className="vg-section-header">
        <p className="vg-section-eyebrow">
          How it works
        </p>

        <h2 className="vg-section-title">
          One assessment, five stages,
          in a fixed order
        </h2>

        <p className="vg-section-lead">
          VendorGuard attempts an ADK{" "}
          <code className="vg-code">
            SequentialAgent
          </code>{" "}
          workflow. Each stage consumes the
          structured result of the previous
          stage. If the external model is
          unavailable, deterministic
          controls safely complete the
          assessment.
        </p>
      </div>

      <div className="vg-pipeline">
        <div
          className="vg-pipeline-line"
          aria-hidden="true"
        />

        {PIPELINE_STEPS.map((step) => (
          <article
            className={`vg-pipeline-step vg-accent-${step.accent}`}
            key={step.step}
          >
            <div className="vg-pipeline-dot" />

            <span className="vg-pipeline-number">
              {step.step}
            </span>

            <h3>
              {step.title}
            </h3>

            <p>
              {step.text}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}


function ArchitectureSection() {
  return (
    <section
      id="architecture"
      className="vg-section vg-section-alt"
    >
      <div className="vg-architecture-header">
        <div className="vg-architecture-copy">
          <p className="vg-section-eyebrow">
            Architecture
          </p>

          <h2 className="vg-section-title">
            What runs behind each
            assessment
          </h2>

          <p className="vg-section-lead">
            The vendors and documents are
            synthetic demonstration data.
            The workflow, policy checks,
            audit trail, fallback controls,
            persistence, and human-review
            gate are implemented application
            features.
          </p>
        </div>

        <div className="vg-architecture-summary">
          <div>
            <span>Frontend</span>
            <strong>React + Vite</strong>
          </div>

          <div>
            <span>Backend</span>
            <strong>FastAPI</strong>
          </div>

          <div>
            <span>Persistence</span>
            <strong>SQLite</strong>
          </div>

          <div>
            <span>Governance</span>
            <strong>ADK + MCP</strong>
          </div>
        </div>
      </div>

      <div className="vg-stack">
        {ARCHITECTURE_LAYERS.map(
          (layer, index) => (
            <article
              className="vg-stack-row"
              key={layer.label}
            >
              <span className="vg-stack-index">
                {String(index + 1).padStart(
                  2,
                  "0",
                )}
              </span>

              <div>
                <h3>
                  {layer.label}
                </h3>

                <p>
                  {layer.detail}
                </p>
              </div>

              {index <
                ARCHITECTURE_LAYERS.length -
                  1 && (
                <span
                  className="vg-stack-arrow"
                  aria-hidden="true"
                >
                  ↓
                </span>
              )}
            </article>
          ),
        )}
      </div>
    </section>
  );
}


function SecuritySection() {
  return (
    <section
      id="security"
      className="vg-section"
    >
      <div className="vg-section-header vg-security-header">
        <p className="vg-section-eyebrow">
          Security
        </p>

        <h2 className="vg-section-title">
          Vendor documents are evidence.
          They are never instructions.
        </h2>

        <p className="vg-section-lead">
          Every vendor-controlled document
          is treated as untrusted content.
          Instructions found inside a
          document are recorded as security
          findings rather than executed.
          DataQuick demonstrates this
          defensive boundary.
        </p>
      </div>

      <div className="vg-security-grid">
        <div className="vg-terminal">
          <div className="vg-terminal-bar">
            <span className="vg-dot vg-dot-red" />
            <span className="vg-dot vg-dot-amber" />
            <span className="vg-dot vg-dot-green" />

            <span className="vg-terminal-title">
              audit_trail.log
            </span>
          </div>

          <pre className="vg-terminal-body">
{`INJECTION_DETECTED | source=security_questionnaire.txt
STATUS = BLOCKED_NOT_EXECUTED

FINDING | severity=critical
  type   = prompt_injection
  action = recorded_for_audit_only
  effect = requires_human_escalation

CONTROL = vendor_content_is_untrusted
HUMAN_REVIEW_REQUIRED = true`}
          </pre>
        </div>

        <div className="vg-security-points">
          {SECURITY_POINTS.map((point) => (
            <article
              className="vg-security-point"
              key={point.title}
            >
              <div className="vg-security-point-icon">
                ✓
              </div>

              <div>
                <h3>
                  {point.title}
                </h3>

                <p>
                  {point.text}
                </p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}


function VendorSection({
  vendors,
  loading,
  startingVendorId,
  onSelect,
}) {
  return (
    <section
      id="vendors"
      className="vg-section vg-section-alt"
    >
      <div className="vg-vendor-header">
        <div>
          <p className="vg-section-eyebrow">
            Synthetic demonstration
          </p>

          <h2 className="vg-section-title">
            Select a vendor
          </h2>

          <p className="vg-section-lead">
            Three synthetic vendors
            demonstrate low-, medium-, and
            high-risk onboarding outcomes.
            DataQuick includes a
            prompt-injection attempt and
            contradictory evidence.
          </p>
        </div>

        <div className="vg-vendor-legend">
          <span className="vg-legend-low">
            Low risk
          </span>

          <span className="vg-legend-medium">
            Medium risk
          </span>

          <span className="vg-legend-high">
            High risk
          </span>
        </div>
      </div>

      {loading ? (
        <div className="vg-vendor-loading">
          Loading demonstration vendors...
        </div>
      ) : vendors.length === 0 ? (
        <div className="vg-empty-state">
          <strong>
            No vendors are available.
          </strong>

          <span>
            Confirm that the backend is
            running on port 8000.
          </span>
        </div>
      ) : (
        <div className="vg-vendor-grid">
          {vendors.map((vendor) => {
            const tierClass =
              String(
                vendor.risk_tier ||
                  "LOW",
              ).toLowerCase();

            const isStarting =
              startingVendorId ===
              vendor.vendor_id;

            return (
              <article
                key={vendor.vendor_id}
                className={`vg-vendor-card vg-vendor-${tierClass}`}
              >
                <div className="vg-vendor-card-top">
                  <span className="vg-risk-pill">
                    {vendor.risk_tier} RISK
                  </span>

                  <span className="vg-vendor-arrow">
                    ↗
                  </span>
                </div>

                <h3>
                  {vendor.name}
                </h3>

                <p>
                  {vendor.description}
                </p>

                <div className="vg-vendor-card-footer">
                  <span>
                    Human review required
                  </span>

                  <button
                    type="button"
                    disabled={Boolean(
                      startingVendorId,
                    )}
                    onClick={() =>
                      onSelect(vendor)
                    }
                  >
                    {isStarting
                      ? "Running assessment..."
                      : "Start assessment"}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}


function SiteFooter() {
  return (
    <footer className="vg-footer">
      <div className="vg-footer-inner">
        <div>
          <a
            href="#top"
            className="vg-footer-brand"
          >
            <span className="vg-nav-logo-mark" />
            VendorGuard AI
          </a>

          <p>
            A demonstration
            decision-support tool. It does
            not certify real organisations
            or replace legal, procurement,
            compliance, or security
            professionals.
          </p>
        </div>

        <div className="vg-footer-links">
          <a
            href="https://github.com/agrima150103/vendorguard-ai"
            target="_blank"
            rel="noreferrer"
          >
            GitHub repository
          </a>

          <a
            href="https://github.com/agrima150103/vendorguard-ai"
            target="_blank"
            rel="noreferrer"
          >
            Project documentation
          </a>

          <a href="#top">
            Back to top
          </a>
        </div>
      </div>
    </footer>
  );
}

