import type { Skill } from "../types/api";

type Props = {
  title: string;
  icon?: string;
  skills: Skill[];
  highlight?: boolean;
};

const IMPORTANCE_CLASS: Record<string, string> = {
  critical: "badge-red",
  high: "badge-orange",
  medium: "badge-amber",
  low: "badge-muted",
};

export function SkillList({ title, icon, skills, highlight }: Props) {
  return (
    <div className={`skill-list-panel ${highlight ? "skill-list-highlight" : ""}`}>
      <h3 className="skill-list-title">
        {icon && <span className="skill-list-icon">{icon}</span>}
        {title}
        <span className="skill-list-count">{skills.length}</span>
      </h3>
      {skills.length === 0 ? (
        <p className="muted-text">None identified.</p>
      ) : (
        <ul className="skill-items">
          {skills.map((skill) => (
            <li key={skill.skill_id || skill.name} className="skill-item">
              <div className="skill-item-header">
                <span className="skill-name">{skill.name}</span>
                <span className={`badge badge-sm ${IMPORTANCE_CLASS[skill.importance] ?? "badge-muted"}`}>
                  {skill.importance}
                </span>
              </div>
              {skill.category && (
                <span className="skill-category">{skill.category}</span>
              )}
              {skill.evidence && (
                <p className="skill-evidence">"{skill.evidence}"</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
