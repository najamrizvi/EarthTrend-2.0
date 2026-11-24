
import './HomePage.css'

export default function HomePage({ onLaunch }) {
  return (
    <main className="home-page">
      <nav className="home-nav">
        <a className="home-brand" href="#home">
          <span className="brand-symbol">E</span>
          <span>
            <strong>EARTH<span>TREND</span></strong>
            <small>EARTH OBSERVATION INTELLIGENCE</small>
          </span>
        </a>

        <div className="home-nav-links">
          <a href="#mission">Mission</a>
          <a href="#capabilities">Capabilities</a>
          <a href="#data">Data & Science</a>
        </div>

        <button className="nav-launch" onClick={onLaunch}>
          Launch Platform <span>↗</span>
        </button>
      </nav>

      <section className="home-hero" id="home">
        <div className="hero-stars" />

        <div className="hero-content">
          <div className="hero-kicker">
            <span className="live-indicator" />
            EARTH OBSERVATION & ENVIRONMENTAL INTELLIGENCE
          </div>

          <h1>
            Understand
            <br />
            <span>Our Changing</span>
            <br />
            Planet.
          </h1>

          <p>
            Explore Earth through satellite observations, geographic
            intelligence and scientific investigation. Discover the
            environmental patterns shaping our planet.
          </p>

          <div className="hero-actions">
            <button className="hero-primary" onClick={onLaunch}>
              Explore EarthTrend <span>↗</span>
            </button>
            <a className="hero-secondary" href="#mission">
              Discover the mission <span>↓</span>
            </a>
          </div>

          <div className="hero-metrics">
            <div>
              <strong>GPM IMERG</strong>
              <span>SATELLITE DATA SOURCE</span>
            </div>
            <div>
              <strong>0.1°</strong>
              <span>SPATIAL RESOLUTION</span>
            </div>
            <div>
              <strong>30 MIN</strong>
              <span>OBSERVATION INTERVAL</span>
            </div>
          </div>
        </div>

        <div className="earth-visual" aria-label="Illustration of Earth viewed from space">
          <div className="earth-orbit orbit-one" />
          <div className="earth-orbit orbit-two" />
          <div className="earth-globe">
            <div className="earth-atmosphere" />
            <div className="earth-surface" />
            <div className="earth-clouds" />
          </div>
          <div className="satellite-marker">
            <span>✦</span>
          </div>
          <div className="earth-caption">
            <span>PLANETARY OBSERVATION</span>
            <strong>EARTH / 001</strong>
          </div>
        </div>

        <div className="hero-bottom-label">
          <span>SCIENTIFIC EXPLORATION</span>
          <span>01 — EARTH SYSTEMS</span>
        </div>
      </section>

      <section className="mission-section" id="mission">
        <div className="section-kicker">01 / OUR MISSION</div>

        <div className="mission-layout">
          <h2>
            Science begins
            <br />
            with <span>observation.</span>
          </h2>

          <div className="mission-description">
            <p>
              EarthTrend 2.0 is an Earth-observation and environmental
              intelligence platform designed to investigate our planet
              through scientific satellite data and geographic analysis.
            </p>
            <p>
              Our goal is to make environmental observations more
              accessible, traceable and meaningful through a unified
              scientific workspace.
            </p>
          </div>
        </div>
      </section>

      <section className="capabilities-section" id="capabilities">
        <div className="section-kicker">02 / PLATFORM CAPABILITIES</div>
        <h2>Explore Earth from a new perspective.</h2>

        <div className="capability-grid">
          <article className="capability-card">
            <span className="capability-number">01</span>
            <div className="capability-icon">◎</div>
            <h3>Geospatial Intelligence</h3>
            <p>
              Investigate geographic regions through interactive maps
              and spatially referenced observations.
            </p>
          </article>

          <article className="capability-card">
            <span className="capability-number">02</span>
            <div className="capability-icon">⌁</div>
            <h3>Satellite Observations</h3>
            <p>
              Explore precipitation measurements from NASA GPM IMERG
              satellite-derived datasets.
            </p>
          </article>

          <article className="capability-card">
            <span className="capability-number">03</span>
            <div className="capability-icon">◷</div>
            <h3>Temporal Investigation</h3>
            <p>
              Examine observations across time and investigate
              environmental changes.
            </p>
          </article>

          <article className="capability-card">
            <span className="capability-number">04</span>
            <div className="capability-icon">✧</div>
            <h3>Scientific Intelligence</h3>
            <p>
              Build toward evidence-backed analysis, forecasting
              and explainable environmental insights.
            </p>
          </article>
        </div>
      </section>

      <section className="science-section" id="data">
        <div className="science-visual">
          <div className="science-ring ring-one" />
          <div className="science-ring ring-two" />
          <div className="science-core">GPM</div>
          <span className="science-coordinate">NASA / IMERG / V07</span>
        </div>

        <div className="science-content">
          <div className="section-kicker">03 / SCIENTIFIC FOUNDATION</div>
          <h2>
            Grounded in
            <br />
            <span>real observations.</span>
          </h2>
          <p>
            The current EarthTrend scientific workflow integrates
            NASA's Global Precipitation Measurement (GPM) mission
            and its IMERG Final Half-Hourly Version 07 dataset.
          </p>
          <div className="science-facts">
            <div>
              <span>DATASET</span>
              <strong>GPM IMERG V07</strong>
            </div>
            <div>
              <span>OBSERVATION</span>
              <strong>Half-hourly</strong>
            </div>
            <div>
              <span>SPATIAL GRID</span>
              <strong>0.1° × 0.1°</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="launch-section">
        <div className="section-kicker">04 / BEGIN EXPLORATION</div>
        <h2>
          The planet is your
          <br />
          <span>field of investigation.</span>
        </h2>
        <p>
          Enter the EarthTrend scientific workspace and explore
          satellite-derived environmental observations.
        </p>
        <button className="hero-primary" onClick={onLaunch}>
          Launch EarthTrend 2.0 <span>↗</span>
        </button>
      </section>

      <footer className="home-footer">
        <div className="home-brand">
          <span className="brand-symbol">E</span>
          <span>
            <strong>EARTH<span>TREND</span></strong>
            <small>EARTH OBSERVATION INTELLIGENCE</small>
          </span>
        </div>
        <span>EARTH TREND 2.0 · SCIENTIFIC PLATFORM</span>
        <a href="#home">BACK TO TOP ↑</a>
      </footer>
    </main>
  )
}
