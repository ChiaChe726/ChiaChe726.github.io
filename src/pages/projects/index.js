import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import Translate, {translate} from '@docusaurus/Translate';
import styles from './styles.module.css';

/**
 * 作品集 — 要新增/修改專案,改這個陣列即可。
 *   emoji — 卡片上方的圖示(之後可換成專案截圖)
 *   title — 專案名稱
 *   description — 一段說明(用 <Translate> 包住才能雙語)
 *   tags  — 技術標籤
 *   link  — 專案連結(GitHub / Demo);沒有就設 null,按鈕會隱藏
 */
const projects = [
  {
    emoji: '🌐',
    title: <Translate id="projects.p1.title">個人網站</Translate>,
    description: (
      <Translate id="projects.p1.desc">
        用 Docusaurus 打造的雙語個人網站,支援亮暗色系與液態玻璃設計。
      </Translate>
    ),
    tags: ['React', 'Docusaurus', 'CSS'],
    link: 'https://github.com/ChiaChe726/ChiaChe726.github.io',
  },
  {
    emoji: '📱',
    title: <Translate id="projects.p2.title">範例專案二</Translate>,
    description: (
      <Translate id="projects.p2.desc">
        這是一個範例專案。把這裡換成你真正做過的作品說明。
      </Translate>
    ),
    tags: ['Node.js', 'API'],
    link: null,
  },
  {
    emoji: '🤖',
    title: <Translate id="projects.p3.title">範例專案三</Translate>,
    description: (
      <Translate id="projects.p3.desc">
        這是一個範例專案。描述你解決了什麼問題、用了哪些技術。
      </Translate>
    ),
    tags: ['Python', 'ML'],
    link: null,
  },
];

function ProjectCard({emoji, title, description, tags, link}) {
  return (
    <div className={clsx('col col--4', styles.col)}>
      <div className={clsx('glass glass-hover', styles.card)}>
        <div className={styles.cardEmoji} aria-hidden="true">
          {emoji}
        </div>
        <Heading as="h3" className={styles.cardTitle}>
          {title}
        </Heading>
        <p className={styles.cardDesc}>{description}</p>
        <div className={styles.tags}>
          {tags.map((tag) => (
            <span key={tag} className={styles.tag}>
              {tag}
            </span>
          ))}
        </div>
        {link && (
          <Link className={clsx('button button--primary', styles.cardBtn)} to={link}>
            <Translate id="projects.viewButton">查看專案 →</Translate>
          </Link>
        )}
      </div>
    </div>
  );
}

export default function Projects() {
  return (
    <Layout
      title={translate({id: 'projects.meta.title', message: '作品集'})}
      description={translate({
        id: 'projects.meta.description',
        message: '我做過的專案與作品。',
      })}>
      <main className={clsx('container', styles.wrapper)}>
        <Heading as="h1" className={styles.pageTitle}>
          <Translate id="projects.title">作品集</Translate>
        </Heading>
        <p className={styles.pageSubtitle}>
          <Translate id="projects.subtitle">
            以下是我做過的一些專案。點擊卡片可以看更多。
          </Translate>
        </p>
        <div className="row">
          {projects.map((p, idx) => (
            <ProjectCard key={idx} {...p} />
          ))}
        </div>
      </main>
    </Layout>
  );
}
