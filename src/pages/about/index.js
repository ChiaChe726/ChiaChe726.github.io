import clsx from 'clsx';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import Translate, {translate} from '@docusaurus/Translate';
import styles from './styles.module.css';

/**
 * 技能列表 — 要新增/修改技能,改這個陣列即可。
 */
const skills = [
  'JavaScript / TypeScript',
  'React',
  'Node.js',
  'Python',
  'HTML / CSS',
  'Git',
  'SQL',
  'Docker',
];

/**
 * 簡歷時間軸 — 每一筆是一段經歷。要替換成真實學經歷,改這個陣列。
 *   period — 期間
 *   title  — 職稱 / 學位(用 <Translate> 包住才能雙語)
 *   org    — 公司 / 學校
 *   desc   — 簡短說明
 */
const timeline = [
  {
    period: <Translate id="about.tl.job1.period">2023 — 現在</Translate>,
    title: <Translate id="about.tl.job1.title">軟體工程師</Translate>,
    org: <Translate id="about.tl.job1.org">某科技公司</Translate>,
    desc: (
      <Translate id="about.tl.job1.desc">
        負責產品的前後端開發與維護,參與從設計到上線的完整流程。
      </Translate>
    ),
  },
  {
    period: <Translate id="about.tl.edu1.period">2019 — 2023</Translate>,
    title: <Translate id="about.tl.edu1.title">資訊工程學士</Translate>,
    org: <Translate id="about.tl.edu1.org">某大學</Translate>,
    desc: (
      <Translate id="about.tl.edu1.desc">
        主修資訊工程,專注於軟體開發與資料結構,並參與多個專題實作。
      </Translate>
    ),
  },
];

export default function About() {
  return (
    <Layout
      title={translate({id: 'about.meta.title', message: '關於我'})}
      description={translate({
        id: 'about.meta.description',
        message: '自我介紹、技能與簡歷。',
      })}>
      <main className={clsx('container', styles.wrapper)}>
        <Heading as="h1" className={styles.pageTitle}>
          <Translate id="about.title">關於我</Translate>
        </Heading>

        {/* 自我介紹 */}
        <section className={clsx('glass', styles.introCard)}>
          <p className={styles.introText}>
            <Translate id="about.intro1">
              我是一位熱愛打造產品的軟體工程師。喜歡把複雜的問題拆解成簡單、優雅的解法,並且重視使用者體驗。
            </Translate>
          </p>
          <p className={styles.introText}>
            <Translate id="about.intro2">
              工作之餘,我喜歡學習新技術、寫技術筆記,也享受把點子實作出來的過程。歡迎透過下方連結與我聯繫!
            </Translate>
          </p>
        </section>

        {/* 技能 */}
        <Heading as="h2" className={styles.sectionTitle}>
          <Translate id="about.skills.title">技能</Translate>
        </Heading>
        <div className={styles.skillTags}>
          {skills.map((skill) => (
            <span key={skill} className={clsx('glass', styles.skillTag)}>
              {skill}
            </span>
          ))}
        </div>

        {/* 簡歷時間軸 */}
        <Heading as="h2" className={styles.sectionTitle}>
          <Translate id="about.timeline.title">學經歷</Translate>
        </Heading>
        <div className={styles.timeline}>
          {timeline.map((item, idx) => (
            <div key={idx} className={clsx('glass', styles.tlItem)}>
              <div className={styles.tlPeriod}>{item.period}</div>
              <div className={styles.tlBody}>
                <Heading as="h3" className={styles.tlTitle}>
                  {item.title}
                </Heading>
                <div className={styles.tlOrg}>{item.org}</div>
                <p className={styles.tlDesc}>{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </main>
    </Layout>
  );
}
