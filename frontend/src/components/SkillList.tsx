import type { Skill } from "../types/api";

type Props = {
  title: string;
  skills: Skill[];
};

export function SkillList({ title, skills }: Props) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {skills.length === 0 ? (
        <p className="muted">No skills detected yet.</p>
      ) : (
        <ul className="skill-list">
          {skills.map((skill) => (
            <li key={`${title}-${skill.skill_id}`}>
              <strong>{skill.name}</strong>
              <span>{skill.category}</span>
              <small>{skill.importance}</small>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
