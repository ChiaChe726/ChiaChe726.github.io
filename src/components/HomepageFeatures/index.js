import clsx from 'clsx';
import Heading from '@theme/Heading';
import Translate from '@docusaurus/Translate';
import styles from './styles.module.css';

/**
 * 首頁亮點區。要替換內容,改下面這個陣列即可:
 *   icon  — 顯示的 emoji(或之後換成圖示)
 *   title — 卡片標題(用 <Translate> 包住才能雙語)
 *   description — 卡片說明
 */
const FeatureList = [
  {
    icon: '🛠️',
    title: <Translate id="features.build.title">打造產品</Translate>,
    description: (
      <Translate id="features.build.desc">
        從零到一把想法做成好用的產品,注重使用體驗與細節。
      </Translate>
    ),
  },
  {
    icon: '⚡',
    title: <Translate id="features.code.title">技術實作</Translate>,
    description: (
      <Translate id="features.code.desc">
        熟悉前後端開發,喜歡用乾淨、可維護的程式碼解決真實問題。
      </Translate>
    ),
  },
  {
    icon: '🌱',
    title: <Translate id="features.learn.title">持續學習</Translate>,
    description: (
      <Translate id="features.learn.desc">
        保持好奇心,把學到的東西寫成筆記與文章,也樂於分享。
      </Translate>
    ),
  },
];

function Feature({icon, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className={clsx('glass glass-hover', styles.card)}>
        <div className={styles.cardIcon} role="img" aria-hidden="true">
          {icon}
        </div>
        <Heading as="h3" className={styles.cardTitle}>
          {title}
        </Heading>
        <p className={styles.cardDesc}>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
