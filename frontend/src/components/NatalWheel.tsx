import { useState } from 'react';

export interface PlanetPosition {
  name: string;
  name_ru: string;
  sign: string;
  sign_index: number;
  degree: number;
  abs_degree: number;
  nakshatra_index: number;
  pada: number;
  is_retrograde: boolean;
  glyph: string;
  color: string;
}

export interface AspectData {
  planet1: string;
  planet2: string;
  aspect: string;
  name_ru: string;
  symbol: string;
  angle: number;
  orb: number;
  nature: 'harmonious' | 'challenging' | 'neutral';
}

export interface HouseCusp {
  house: number;
  longitude: number;
  sign: string;
  sign_index: number;
  degree: number;
}

interface NatalWheelProps {
  planets: PlanetPosition[];
  houses: HouseCusp[];
  ascendant: { longitude: number; sign: string; degree: number };
  mc?: { longitude: number; sign: string; degree: number };
  aspects: AspectData[];
  onSelectPlanet?: (planet: PlanetPosition) => void;
  selectedPlanet?: string | null;
}

const ZODIAC_SIGNS = [
  { symbol: '♈', name_ru: 'Овен', element: 'fire', color: '#E05D5D' },
  { symbol: '♉', name_ru: 'Телец', element: 'earth', color: '#5DB88C' },
  { symbol: '♊', name_ru: 'Близнецы', element: 'air', color: '#E8C75A' },
  { symbol: '♋', name_ru: 'Рак', element: 'water', color: '#5B8DEF' },
  { symbol: '♌', name_ru: 'Лев', element: 'fire', color: '#E05D5D' },
  { symbol: '♍', name_ru: 'Дева', element: 'earth', color: '#5DB88C' },
  { symbol: '♎', name_ru: 'Весы', element: 'air', color: '#E8C75A' },
  { symbol: '♏', name_ru: 'Скорпион', element: 'water', color: '#5B8DEF' },
  { symbol: '♐', name_ru: 'Стрелец', element: 'fire', color: '#E05D5D' },
  { symbol: '♑', name_ru: 'Козерог', element: 'earth', color: '#5DB88C' },
  { symbol: '♒', name_ru: 'Водолей', element: 'air', color: '#E8C75A' },
  { symbol: '♓', name_ru: 'Рыбы', element: 'water', color: '#5B8DEF' },
];

export function NatalWheel({
  planets,
  houses,
  ascendant,
  mc,
  aspects,
  onSelectPlanet,
  selectedPlanet,
}: NatalWheelProps) {
  const [zoom, setZoom] = useState(1);
  const [hoveredPlanet, setHoveredPlanet] = useState<PlanetPosition | null>(null);
  const [hoveredAspect, setHoveredAspect] = useState<AspectData | null>(null);

  const size = 560;
  const cx = size / 2;
  const cy = size / 2;

  // Concentric circle radii
  const rOuter = 265;
  const rZodiacOuter = 260;
  const rZodiacInner = 222;
  const rHouseOuter = 222;
  const rHouseInner = 158;
  const rAspect = 145;
  const rCenter = 32;

  // Chart rotation: align Ascendant to 180° (standard 9 o'clock position on astrology wheels)
  // Angle in SVG: 0° is 3 o'clock (positive X axis), clockwise is positive in standard screen coords
  // In astrology, counter-clockwise goes through Aries->Taurus, or clockwise depending on orientation.
  // We use standard counter-clockwise celestial motion mapped with Ascendant at 180° (west / left).
  const ascLon = ascendant ? ascendant.longitude : 0;
  const lonToAngle = (lon: number) => {
    // lon = ascLon maps to 180 deg (left)
    // As lon increases, it rotates counter-clockwise
    const angle = 180 - (lon - ascLon);
    return ((angle % 360) + 360) % 360;
  };

  const polarToCartesian = (radius: number, angleInDegrees: number) => {
    const radians = (angleInDegrees * Math.PI) / 180.0;
    return {
      x: cx + radius * Math.cos(radians),
      y: cy + radius * Math.sin(radians),
    };
  };

  // Group planets that are very close to prevent overlapping glyphs
  const sortedPlanets = [...planets].sort((a, b) => a.abs_degree - b.abs_degree);
  const planetVisualAngles: Record<string, number> = {};
  for (let i = 0; i < sortedPlanets.length; i++) {
    const p = sortedPlanets[i];
    let baseAngle = lonToAngle(p.abs_degree);
    // check distance to previously placed planet
    if (i > 0) {
      const prev = sortedPlanets[i - 1];
      const prevAngle = planetVisualAngles[prev.name];
      let diff = Math.abs(baseAngle - prevAngle);
      if (diff > 180) diff = 360 - diff;
      if (diff < 12) {
        baseAngle = (prevAngle - 13 + 360) % 360;
      }
    }
    planetVisualAngles[p.name] = baseAngle;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', position: 'relative' }}>
      {/* Zoom / Controls bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        width: '100%',
        marginBottom: '10px',
        padding: '0 4px',
        fontSize: '0.8rem',
        color: 'var(--text-secondary)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ color: 'var(--accent-gold)', fontWeight: 600 }}>АСЦ:</span>
          <span>{ascendant ? `${ascendant.degree.toFixed(1)}° ${ascendant.sign}` : '—'}</span>
          {mc && (
            <>
              <span style={{ color: 'var(--text-muted)' }}>•</span>
              <span style={{ color: 'var(--accent-gold-light)', fontWeight: 600 }}>MC:</span>
              <span>{`${mc.degree.toFixed(1)}° ${mc.sign}`}</span>
            </>
          )}
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            onClick={() => setZoom(Math.max(0.8, zoom - 0.1))}
            style={{
              background: 'var(--bg-card-secondary)',
              border: '1px solid var(--border-card)',
              color: 'var(--text-main)',
              borderRadius: '4px',
              padding: '2px 8px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            −
          </button>
          <span style={{ padding: '2px 4px' }}>{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => setZoom(Math.min(1.4, zoom + 0.1))}
            style={{
              background: 'var(--bg-card-secondary)',
              border: '1px solid var(--border-card)',
              color: 'var(--text-main)',
              borderRadius: '4px',
              padding: '2px 8px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            +
          </button>
          <button
            onClick={() => setZoom(1)}
            style={{
              background: 'var(--bg-card-secondary)',
              border: '1px solid var(--border-card)',
              color: 'var(--text-secondary)',
              borderRadius: '4px',
              padding: '2px 6px',
              cursor: 'pointer',
              fontSize: '0.75rem'
            }}
          >
            Сброс
          </button>
        </div>
      </div>

      {/* SVG Container */}
      <div style={{
        width: '100%',
        maxWidth: `${size}px`,
        overflow: 'visible',
        display: 'flex',
        justifyContent: 'center'
      }}>
        <svg
          viewBox={`0 0 ${size} ${size}`}
          style={{
            width: '100%',
            height: 'auto',
            transform: `scale(${zoom})`,
            transition: 'transform 0.2s ease',
            filter: 'drop-shadow(0 8px 30px rgba(0,0,0,0.6))'
          }}
        >
          <defs>
            {/* Background Glow */}
            <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#DDBA48" stopOpacity="0.12" />
              <stop offset="60%" stopColor="#141521" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#080B14" stopOpacity="1" />
            </radialGradient>
            <radialGradient id="goldRing" cx="50%" cy="50%" r="50%">
              <stop offset="85%" stopColor="#161826" />
              <stop offset="98%" stopColor="#222436" />
              <stop offset="100%" stopColor="#DDBA48" stopOpacity="0.5" />
            </radialGradient>
          </defs>

          {/* Background disks */}
          <circle cx={cx} cy={cy} r={rOuter} fill="#0B0D18" stroke="var(--border-card)" strokeWidth="1" />
          <circle cx={cx} cy={cy} r={rZodiacOuter} fill="url(#goldRing)" stroke="rgba(221, 186, 72, 0.4)" strokeWidth="1" />
          <circle cx={cx} cy={cy} r={rZodiacInner} fill="#0E101D" stroke="rgba(221, 186, 72, 0.3)" strokeWidth="1" />
          <circle cx={cx} cy={cy} r={rHouseInner} fill="#090B14" stroke="rgba(255, 255, 255, 0.08)" strokeWidth="1" />
          <circle cx={cx} cy={cy} r={rAspect} fill="url(#centerGlow)" stroke="rgba(221, 186, 72, 0.15)" strokeWidth="1" strokeDasharray="3,3" />

          {/* 12 Zodiac Segments (30° each in Sidereal lahiri) */}
          {ZODIAC_SIGNS.map((sign, index) => {
            const startLon = index * 30;
            const midLon = index * 30 + 15;
            const startAngle = lonToAngle(startLon);
            const midAngle = lonToAngle(midLon);

            // Boundary separator lines in Zodiac ring
            const p1 = polarToCartesian(rZodiacInner, startAngle);
            const p2 = polarToCartesian(rZodiacOuter, startAngle);

            // Midpoint position for Sign Symbol
            const symbolPos = polarToCartesian((rZodiacOuter + rZodiacInner) / 2, midAngle);

            return (
              <g key={`sign-${index}`}>
                {/* Sector border */}
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke="rgba(255, 255, 255, 0.12)"
                  strokeWidth="1"
                />
                {/* Zodiac Sign Symbol */}
                <text
                  x={symbolPos.x}
                  y={symbolPos.y + 5}
                  textAnchor="middle"
                  fill={sign.color}
                  fontSize="17"
                  fontFamily="-apple-system, BlinkMacSystemFont, sans-serif"
                  fontWeight="600"
                  style={{ userSelect: 'none', cursor: 'default' }}
                >
                  {sign.symbol}
                </text>
              </g>
            );
          })}

          {/* 12 House Cusps & Division Lines */}
          {houses && houses.length === 12 && houses.map((h, i) => {
            const cuspAngle = lonToAngle(h.longitude);
            const pInner = polarToCartesian(rAspect, cuspAngle);
            const pOuter = polarToCartesian(rZodiacInner, cuspAngle);

            // House number label placed midway between current cusp and next cusp
            const nextCusp = houses[(i + 1) % 12];
            let span = (nextCusp.longitude - h.longitude + 360) % 360;
            const houseMidLon = (h.longitude + span / 2) % 360;
            const houseMidAngle = lonToAngle(houseMidLon);
            const labelPos = polarToCartesian((rHouseOuter + rHouseInner) / 2, houseMidAngle);

            const isAngular = [1, 4, 7, 10].includes(h.house);

            return (
              <g key={`house-cusp-${h.house}`}>
                {/* House line */}
                <line
                  x1={pInner.x}
                  y1={pInner.y}
                  x2={pOuter.x}
                  y2={pOuter.y}
                  stroke={isAngular ? 'rgba(221, 186, 72, 0.55)' : 'rgba(255, 255, 255, 0.1)'}
                  strokeWidth={isAngular ? '1.5' : '1'}
                  strokeDasharray={isAngular ? undefined : '2,3'}
                />
                {/* House Roman / Arabic number */}
                <text
                  x={labelPos.x}
                  y={labelPos.y + 4}
                  textAnchor="middle"
                  fill={isAngular ? 'var(--accent-gold)' : 'var(--text-muted)'}
                  fontSize={isAngular ? '11' : '10'}
                  fontWeight={isAngular ? '700' : '500'}
                  opacity={0.85}
                  style={{ userSelect: 'none' }}
                >
                  {h.house}
                </text>
              </g>
            );
          })}

          {/* Ascendant Axis (180° standard - West line across to East) */}
          <line
            x1={cx - rZodiacOuter}
            y1={cy}
            x2={cx + rZodiacOuter}
            y2={cy}
            stroke="rgba(221, 186, 72, 0.6)"
            strokeWidth="1.5"
            strokeDasharray="4,3"
          />
          {/* ASC tag */}
          <rect
            x={cx - rZodiacOuter - 3}
            y={cy - 9}
            width="26"
            height="18"
            rx="3"
            fill="var(--accent-gold)"
          />
          <text
            x={cx - rZodiacOuter + 10}
            y={cy + 4}
            textAnchor="middle"
            fill="#080B14"
            fontSize="10"
            fontWeight="bold"
          >
            AC
          </text>
          {/* DSC tag */}
          <text
            x={cx + rZodiacOuter - 14}
            y={cy + 4}
            textAnchor="middle"
            fill="var(--text-secondary)"
            fontSize="9"
            fontWeight="600"
          >
            DC
          </text>

          {/* MC Line if available */}
          {mc && (
            (() => {
              const mcAngle = lonToAngle(mc.longitude);
              const pMc = polarToCartesian(rZodiacOuter, mcAngle);
              const pIc = polarToCartesian(rZodiacOuter, (mcAngle + 180) % 360);
              return (
                <g>
                  <line
                    x1={pMc.x}
                    y1={pMc.y}
                    x2={pIc.x}
                    y2={pIc.y}
                    stroke="rgba(232, 199, 90, 0.5)"
                    strokeWidth="1.2"
                    strokeDasharray="3,3"
                  />
                  <circle cx={pMc.x} cy={pMc.y} r="4" fill="var(--accent-gold-light)" />
                  <text
                    x={pMc.x}
                    y={pMc.y > cy ? pMc.y + 14 : pMc.y - 8}
                    textAnchor="middle"
                    fill="var(--accent-gold-light)"
                    fontSize="9"
                    fontWeight="bold"
                  >
                    MC
                  </text>
                </g>
              );
            })()
          )}

          {/* Aspect Chords in Wheel Center */}
          {aspects.map((asp, idx) => {
            const angle1 = planetVisualAngles[asp.planet1];
            const angle2 = planetVisualAngles[asp.planet2];
            if (angle1 === undefined || angle2 === undefined) return null;

            const p1 = polarToCartesian(rAspect - 5, angle1);
            const p2 = polarToCartesian(rAspect - 5, angle2);

            let strokeColor = 'rgba(255, 255, 255, 0.2)';
            let strokeDash = undefined;
            if (asp.nature === 'harmonious') {
              strokeColor = 'rgba(66, 201, 121, 0.55)'; // Green / Trine / Sextile
            } else if (asp.nature === 'challenging') {
              strokeColor = 'rgba(240, 100, 112, 0.55)'; // Red / Square / Opposition
              if (asp.aspect === 'Opposition') strokeDash = '3,3';
            } else {
              strokeColor = 'rgba(221, 186, 72, 0.55)'; // Gold / Conjunction
            }

            const isHovered = hoveredAspect === asp;

            return (
              <line
                key={`asp-${idx}`}
                x1={p1.x}
                y1={p1.y}
                x2={p2.x}
                y2={p2.y}
                stroke={isHovered ? '#FFF' : strokeColor}
                strokeWidth={isHovered ? 2.5 : 1}
                strokeDasharray={strokeDash}
                onMouseEnter={() => setHoveredAspect(asp)}
                onMouseLeave={() => setHoveredAspect(null)}
                style={{ cursor: 'pointer', transition: 'stroke-width 0.2s' }}
              />
            );
          })}

          {/* Central Core Decorative Compass */}
          <circle cx={cx} cy={cy} r={rCenter} fill="#141521" stroke="var(--border-card)" strokeWidth="1" />
          <circle cx={cx} cy={cy} r={rCenter - 8} fill="#090B14" stroke="rgba(221, 186, 72, 0.3)" strokeWidth="1" />
          <text
            x={cx}
            y={cy + 4}
            textAnchor="middle"
            fill="var(--accent-gold)"
            fontSize="10"
            letterSpacing="1"
            fontWeight="bold"
          >
            LUMIRA
          </text>

          {/* Planet Markers */}
          {planets.map((planet) => {
            const angle = planetVisualAngles[planet.name] ?? lonToAngle(planet.abs_degree);
            const pos = polarToCartesian((rHouseOuter + rHouseInner) / 2 + 10, angle);
            const isSelected = selectedPlanet === planet.name;
            const isHovered = hoveredPlanet?.name === planet.name;

            return (
              <g
                key={`planet-${planet.name}`}
                transform={`translate(${pos.x}, ${pos.y})`}
                onClick={() => onSelectPlanet && onSelectPlanet(planet)}
                onMouseEnter={() => setHoveredPlanet(planet)}
                onMouseLeave={() => setHoveredPlanet(null)}
                style={{ cursor: 'pointer' }}
              >
                {/* Glow ring if selected */}
                {(isSelected || isHovered) && (
                  <circle
                    r="16"
                    fill="rgba(221, 186, 72, 0.2)"
                    stroke="var(--accent-gold)"
                    strokeWidth="1.5"
                  />
                )}
                {/* Planet badge circle */}
                <circle
                  r="12"
                  fill="#141521"
                  stroke={planet.color || 'var(--accent-gold)'}
                  strokeWidth="1.2"
                />
                {/* Planet Glyph */}
                <text
                  textAnchor="middle"
                  y="4"
                  fill={planet.color || 'var(--text-main)'}
                  fontSize="12"
                  fontWeight="bold"
                  fontFamily="-apple-system, BlinkMacSystemFont, sans-serif"
                >
                  {planet.glyph}
                </text>
                {/* Retrograde badge */}
                {planet.is_retrograde && (
                  <text
                    x="8"
                    y="-5"
                    fill="var(--status-error)"
                    fontSize="8"
                    fontWeight="bold"
                  >
                    R
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Hover tooltip for aspect / planet */}
      {(hoveredPlanet || hoveredAspect) && (
        <div style={{
          position: 'absolute',
          bottom: '8px',
          background: 'rgba(17, 17, 29, 0.95)',
          border: '1px solid var(--border-card)',
          borderRadius: '8px',
          padding: '6px 14px',
          fontSize: '0.8rem',
          color: 'var(--text-main)',
          boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
          pointerEvents: 'none',
          zIndex: 10
        }}>
          {hoveredPlanet && (
            <span>
              <strong style={{ color: hoveredPlanet.color }}>{hoveredPlanet.name_ru} ({hoveredPlanet.name})</strong>: {hoveredPlanet.degree.toFixed(2)}° {hoveredPlanet.sign}
              {hoveredPlanet.is_retrograde && <span style={{ color: 'var(--status-error)', marginLeft: '6px' }}>[Ретроградна]</span>}
              <span style={{ color: 'var(--text-secondary)', marginLeft: '8px' }}>Накшатра #{hoveredPlanet.nakshatra_index + 1} (Пада {hoveredPlanet.pada})</span>
            </span>
          )}
          {hoveredAspect && !hoveredPlanet && (
            <span>
              <strong>{hoveredAspect.name_ru} ({hoveredAspect.symbol})</strong>: {hoveredAspect.planet1} ↔ {hoveredAspect.planet2} | Орбис: {hoveredAspect.orb.toFixed(2)}°
            </span>
          )}
        </div>
      )}
    </div>
  );
}
