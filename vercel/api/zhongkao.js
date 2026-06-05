/**
 * 杭州中考志愿填报 API - Vercel Serverless
 * 调用智谱AI GLM-4-Flash，根据多维成绩生成个性化志愿方案
 */

const ZHIPU_API_KEY = process.env.ZHIPU_API_KEY || 'd66eba51f54e4211aed6f9af217ca122.pKK63AJ6GVVRN4xk';

export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') return res.status(200).end();
    if (req.method !== 'POST') return res.status(405).json({ error: '只支持 POST 请求' });

    const { nickname, schoolName, mock1Score, mock1Rank, mock2Score, mock2Rank,
            targets, homeAddress, boarding, grade8bScore, grade8bRank,
            grade9aScore, grade9aRank } = req.body;

    if (!mock1Score && !mock2Score) {
        return res.status(400).json({ error: '请至少提供一模或二模成绩' });
    }
    if (!schoolName) {
        return res.status(400).json({ error: '请填写所在中学名称' });
    }

    const prompt = buildPrompt(req.body);

    try {
        const response = await fetch('https://open.bigmodel.cn/api/paas/v4/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${ZHIPU_API_KEY}`
            },
            body: JSON.stringify({
                model: 'glm-4-flash',
                messages: [
                    {
                        role: 'system',
                        content: `你是杭州中考志愿填报资深顾问，精通2026年杭州中考政策。核心知识：
- 2026年一段线预测567分，重高线622分
- 新增4所县中面向主城区招生
- 中本一体化(ZBTI)分数线涨幅+3~+8分
- 分配生比例约17%，按学校学籍人数计算
- 杭州各区高中梯队清晰：杭二中/学军/杭外(顶尖) → 杭高/十四中/四中(重高) → 浙大附中/长河/杭师大附中(优高) → 源清/杭七中/西湖高级中学等
- 通勤距离和住校条件影响实际志愿选择

回答要求：
1. 先做成绩趋势分析（一模→二模涨跌、各阶段成绩走势）
2. 给出冲/稳/保三梯度志愿推荐，每个学校附理由（分数匹配度+特色+通勤住校匹配）
3. 评估分配生资格
4. 如提供了家庭地址，考虑就近学校推荐
5. 如提供了住校偏好，按偏好筛选学校
6. 末尾附注意事项`
                    },
                    { role: 'user', content: prompt }
                ],
                temperature: 0.7,
                max_tokens: 2500
            })
        });

        if (!response.ok) {
            const err = await response.text();
            return res.status(502).json({ error: 'AI 服务暂时不可用，请稍后重试', detail: err.substring(0, 200) });
        }

        const data = await response.json();
        return res.status(200).json({
            success: true,
            result: data.choices?.[0]?.message?.content || '暂无结果',
            model: 'glm-4-flash',
            usage: data.usage
        });

    } catch (error) {
        return res.status(500).json({ error: '服务异常，请稍后重试' });
    }
}

function buildPrompt(body) {
    const { nickname, schoolName, mock1Score, mock1Rank, mock2Score, mock2Rank,
            targets, homeAddress, boarding, grade8bScore, grade8bRank,
            grade9aScore, grade9aRank } = body;

    let p = '请为以下学生做杭州中考志愿综合分析：\n\n';

    // 基本信息
    p += `【基本信息】\n`;
    if (nickname) p += `- 昵称：${nickname}\n`;
    p += `- 所在中学：${schoolName}\n`;
    p += `- 住校偏好：${boarding || '不限'}\n`;
    if (homeAddress) p += `- 家庭地址：${homeAddress}\n`;

    // 成绩汇总
    p += `\n【成绩数据】\n`;
    if (mock1Score) {
        p += `- 一模：${mock1Score}分`;
        if (mock1Rank) p += `，年级第${mock1Rank}名`;
        p += `\n`;
    }
    if (mock2Score) {
        p += `- 二模：${mock2Score}分`;
        if (mock2Rank) p += `，年级第${mock2Rank}名`;
        p += `\n`;
    }

    // 成绩趋势
    if (mock1Score && mock2Score) {
        const diff = (mock2Score - mock1Score).toFixed(1);
        const trend = diff > 0 ? `上涨${diff}分` : diff < 0 ? `下降${Math.abs(diff)}分` : '持平';
        p += `- 一模→二模趋势：${trend}\n`;
    }

    // 历史成绩
    const hasHistory = grade8bScore || grade9aScore;
    if (hasHistory) {
        p += `\n【历史成绩】\n`;
        if (grade8bScore) {
            p += `- 八下期末：${grade8bScore}分`;
            if (grade8bRank) p += `，年排${grade8bRank}`;
            p += `\n`;
        }
        if (grade9aScore) {
            p += `- 九上期末：${grade9aScore}分`;
            if (grade9aRank) p += `，年排${grade9aRank}`;
            p += `\n`;
        }
        // 整体趋势
        const scores = [grade8bScore, grade9aScore, mock1Score, mock2Score].filter(s => s !== null && s !== undefined);
        if (scores.length >= 2) {
            const trend = scores[scores.length-1] > scores[0] ? '整体呈上升趋势' : '需关注提升空间';
            p += `- 成绩走势：${trend}\n`;
        }
    }

    // 目标偏好
    if (targets) {
        p += `\n【目标偏好】\n`;
        p += `- ${targets}\n`;
    }

    // 参考数据
    p += `\n【2026年杭州中考参考线】\n`;
    p += `- 一段线预测：567分\n`;
    p += `- 重高线预测：622分\n`;
    p += `- 分配生比例：约17%\n`;

    // 输出格式
    p += `\n请按以下结构输出志愿方案：\n`;
    p += `1. 📊 成绩定位与趋势分析\n`;
    p += `2. 🎯 分配生资格评估（基于${schoolName}情况）\n`;
    p += `3. 🏫 冲-稳-保 三梯度志愿推荐（表格形式，含学校名+推荐理由+分数匹配度+通勤/住校匹配）\n`;
    if (homeAddress) p += `4. 🏠 就近学校推荐\n`;
    p += `${homeAddress ? '5' : '4'}. ⚠️ 注意事项与填报策略\n`;

    return p;
}
