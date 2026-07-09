export const IT_ROLES = [
    'Frontend Developer',
    'Backend Developer',
    'Fullstack Developer',
    'AI Engineer',
    'Data Analyst',
    'Data Scientist',
    'DevOps Engineer',
    'QA Engineer',
    'Mobile Developer',
    'Software Engineer Intern',
    'Fresher Software Engineer',
];

export const IT_LEVELS = ['Intern', 'Fresher', 'Junior', 'Middle', 'Senior'];

export const QUESTION_CATEGORIES = [
    'HR / General',
    'Behavioral',
    'Project Deep Dive',
    'CV-based Questions',
    'Job Description-based Questions',
    'Backend',
    'Frontend',
    'Fullstack',
    'Database / SQL',
    'REST API',
    'Authentication / Authorization',
    'System Design',
    'Testing / QA',
    'DevOps',
    'Docker / Deployment',
    'Cloud Basics',
    'Data Analyst',
    'Data Science',
    'AI / Machine Learning',
    'Python',
    'JavaScript',
    'React',
    'Node.js',
    'FastAPI',
    'Security Basics',
    'Performance / Optimization',
    'Git / Teamwork',
    'Intern / Fresher fundamentals',
    'Junior problem solving',
    'Middle/Senior architecture thinking',
];

export const DIFFICULTIES = ['Easy', 'Medium', 'Hard'];

const LEVEL_CONTEXT = {
    Intern: {
        difficulty: 'Easy',
        scope: 'trong bài tập, đồ án hoặc kỳ thực tập',
        evidence: 'một ví dụ học tập hoặc project nhỏ',
        expectation: 'nhà tuyển dụng muốn thấy nền tảng, tư duy học hỏi và cách bạn diễn đạt vấn đề rõ ràng',
    },
    Fresher: {
        difficulty: 'Easy',
        scope: 'trong project cá nhân, đồ án tốt nghiệp hoặc công việc đầu tiên',
        evidence: 'một ví dụ có vai trò cá nhân rõ ràng',
        expectation: 'nhà tuyển dụng muốn thấy bạn hiểu quy trình làm việc thực tế và biết tự kiểm tra kết quả',
    },
    Junior: {
        difficulty: 'Medium',
        scope: 'trong một task sản phẩm có yêu cầu, deadline và phản hồi từ team',
        evidence: 'một ví dụ có trade-off, lỗi phát sinh và kết quả đo được',
        expectation: 'nhà tuyển dụng muốn thấy khả năng tự xử lý vấn đề, giao tiếp và cải thiện sau feedback',
    },
    Middle: {
        difficulty: 'Medium',
        scope: 'trong một tính năng có nhiều module, dữ liệu thật hoặc nhiều người dùng',
        evidence: 'một ví dụ có phân tích nguyên nhân, lựa chọn giải pháp và tác động đến hệ thống',
        expectation: 'nhà tuyển dụng muốn thấy tư duy thiết kế, phối hợp liên team và khả năng chịu trách nhiệm',
    },
    Senior: {
        difficulty: 'Hard',
        scope: 'trong một hệ thống production có ràng buộc về scale, bảo mật, vận hành hoặc chi phí',
        evidence: 'một ví dụ có quyết định kiến trúc, rủi ro, cách đo lường và bài học sau triển khai',
        expectation: 'nhà tuyển dụng muốn thấy năng lực dẫn dắt, ra quyết định dựa trên dữ liệu và quản trị rủi ro',
    },
};

const QUESTION_THEMES = [
    {
        slug: 'self-intro-role-fit',
        category: 'HR / General',
        role: 'Fresher Software Engineer',
        tags: ['giới thiệu bản thân', 'định hướng nghề nghiệp', 'role fit'],
        prompt: 'Bạn hãy giới thiệu bản thân và giải thích vì sao kỹ năng hiện tại phù hợp với vị trí IT này',
        intent: 'kiểm tra khả năng tóm tắt nền tảng, chọn điểm mạnh liên quan và liên kết với vai trò ứng tuyển',
        guidance: 'Nên nói ngắn gọn theo mạch: nền tảng, kỹ năng chính, project tiêu biểu, lý do chọn vai trò và mục tiêu gần.',
    },
    {
        slug: 'career-goal-it',
        category: 'HR / General',
        role: 'Software Engineer Intern',
        tags: ['career goal', 'learning mindset', 'IT role'],
        prompt: 'Mục tiêu nghề nghiệp 1-2 năm tới của bạn trong ngành IT là gì và bạn đang chuẩn bị như thế nào',
        intent: 'kiểm tra mức độ nghiêm túc với ngành, khả năng tự học và sự phù hợp với lộ trình của công ty',
        guidance: 'Nên nêu mục tiêu cụ thể, kỹ năng đang rèn, dự án chứng minh và cách bạn đo tiến bộ.',
    },
    {
        slug: 'production-bug-debug',
        category: 'Junior problem solving',
        role: 'Fullstack Developer',
        tags: ['debugging', 'production bug', 'incident'],
        prompt: 'Khi một bug chỉ xảy ra trên production nhưng không tái hiện được ở local, bạn sẽ debug theo hướng nào',
        intent: 'kiểm tra cách suy luận, thu thập bằng chứng, khoanh vùng lỗi và giao tiếp khi có sự cố',
        guidance: 'Trình bày cách xem log/metric, kiểm tra dữ liệu đầu vào, môi trường, phiên bản deploy, feature flag và cách giảm rủi ro cho người dùng.',
    },
    {
        slug: 'team-conflict',
        category: 'Behavioral',
        role: 'Fullstack Developer',
        tags: ['teamwork', 'conflict', 'communication'],
        prompt: 'Bạn từng xử lý bất đồng kỹ thuật trong nhóm như thế nào và vai trò cụ thể của bạn là gì',
        intent: 'kiểm tra sự trưởng thành, khả năng lắng nghe, lập luận bằng dữ liệu và hướng đến kết quả chung',
        guidance: 'Kể tình huống thật, tránh đổ lỗi, nêu rõ tiêu chí đánh giá phương án và kết quả sau khi thống nhất.',
    },
    {
        slug: 'code-review-feedback',
        category: 'Git / Teamwork',
        role: 'Software Engineer Intern',
        tags: ['code review', 'feedback', 'collaboration'],
        prompt: 'Nếu pull request của bạn bị review nhiều lỗi, bạn sẽ phản hồi và cải thiện như thế nào',
        intent: 'kiểm tra thái độ nhận feedback, kỹ năng đọc review và cách phòng lỗi lặp lại',
        guidance: 'Nêu cách phân loại feedback, hỏi lại khi chưa rõ, sửa có kiểm chứng và rút ra checklist cá nhân.',
    },
    {
        slug: 'project-impact',
        category: 'Project Deep Dive',
        role: 'Fresher Software Engineer',
        tags: ['project', 'ownership', 'impact'],
        prompt: 'Chọn một project trong CV và giải thích đóng góp cá nhân cùng tác động đo được của bạn',
        intent: 'kiểm tra liệu ứng viên thật sự hiểu phần mình làm hay chỉ mô tả chung công việc của nhóm',
        guidance: 'Nêu bối cảnh, phạm vi bạn phụ trách, quyết định kỹ thuật, khó khăn, kết quả và số liệu nếu có.',
    },
    {
        slug: 'cv-gap-testing',
        category: 'CV-based Questions',
        role: 'Frontend Developer',
        tags: ['CV gap', 'testing', 'frontend'],
        prompt: 'CV của bạn liệt kê nhiều công nghệ frontend nhưng ít kinh nghiệm testing. Bạn đã kiểm thử frontend như thế nào',
        intent: 'kiểm tra sự trung thực với khoảng trống CV và khả năng đưa ra kế hoạch cải thiện đáng tin cậy',
        guidance: 'Thừa nhận phạm vi đã làm, nêu ví dụ test thủ công/tự động, bug từng phát hiện và kế hoạch học thêm.',
    },
    {
        slug: 'jd-rest-api-proof',
        category: 'Job Description-based Questions',
        role: 'Backend Developer',
        tags: ['JD', 'REST API', 'evidence'],
        prompt: 'JD yêu cầu kinh nghiệm REST API. Bạn đã xây API nào, xử lý validation và lỗi ra sao',
        intent: 'kiểm tra từ khóa trong CV có gắn với kinh nghiệm thật, không chỉ là liệt kê công nghệ',
        guidance: 'Nêu mục đích API, endpoint chính, cách validate input, mã lỗi, auth, logging và kết quả sử dụng.',
    },
    {
        slug: 'react-rerender',
        category: 'React',
        role: 'Frontend Developer',
        tags: ['React', 'performance', 'render'],
        prompt: 'Nếu một component React render quá nhiều lần, bạn sẽ kiểm tra và xử lý như thế nào',
        intent: 'kiểm tra hiểu biết về state ownership, props stability, memoization và đo lường hiệu năng',
        guidance: 'Bắt đầu bằng DevTools/profiler, xác định nguồn state, tách component, ổn định callback/props và chỉ dùng memo khi có bằng chứng.',
    },
    {
        slug: 'frontend-form-accessibility',
        category: 'Frontend',
        role: 'Frontend Developer',
        tags: ['accessibility', 'form', 'UX'],
        prompt: 'Bạn sẽ kiểm tra accessibility cho một form đăng ký hoặc upload CV như thế nào',
        intent: 'kiểm tra năng lực frontend thực tế ngoài giao diện đẹp',
        guidance: 'Nêu label, keyboard flow, focus state, error message, contrast, aria-live cho trạng thái và test bằng screen reader cơ bản.',
    },
    {
        slug: 'javascript-async-error',
        category: 'JavaScript',
        role: 'Frontend Developer',
        tags: ['JavaScript', 'async', 'error handling'],
        prompt: 'Khi gọi nhiều API bất đồng bộ trên frontend, bạn quản lý loading, lỗi và race condition như thế nào',
        intent: 'kiểm tra khả năng xây UI ổn định khi dữ liệu không đến theo thứ tự mong muốn',
        guidance: 'Nêu trạng thái loading/error riêng, abort/cancel request, kiểm tra request mới nhất và hiển thị retry có kiểm soát.',
    },
    {
        slug: 'css-responsive-layout',
        category: 'Frontend',
        role: 'Frontend Developer',
        tags: ['CSS', 'responsive', 'layout'],
        prompt: 'Bạn xử lý một layout dashboard bị vỡ trên mobile như thế nào',
        intent: 'kiểm tra tư duy layout, breakpoint, overflow và ưu tiên nội dung',
        guidance: 'Nêu cách kiểm tra container, grid/flex, min-width, text wrapping, table responsive và test trên viewport thật.',
    },
    {
        slug: 'backend-auth-authz',
        category: 'Authentication / Authorization',
        role: 'Backend Developer',
        tags: ['authentication', 'authorization', 'security'],
        prompt: 'Giải thích khác nhau giữa authentication và authorization trong một hệ thống web thực tế',
        intent: 'kiểm tra nền tảng bảo mật backend và khả năng áp dụng vào endpoint thật',
        guidance: 'Dùng ví dụ login xác minh danh tính, authorization kiểm quyền truy cập tài nguyên, kèm rủi ro IDOR/RBAC.',
    },
    {
        slug: 'backend-api-design',
        category: 'REST API',
        role: 'Backend Developer',
        tags: ['REST API', 'design', 'versioning'],
        prompt: 'Bạn thiết kế REST API cho tài nguyên CV hoặc job listing như thế nào để dễ mở rộng',
        intent: 'kiểm tra cách đặt resource, HTTP method, status code, pagination, validation và versioning',
        guidance: 'Nêu resource rõ ràng, request/response schema, mã lỗi, filter/sort/pagination và tương thích ngược.',
    },
    {
        slug: 'database-index',
        category: 'Database / SQL',
        role: 'Backend Developer',
        tags: ['SQL', 'index', 'performance'],
        prompt: 'Khi nào bạn thêm index vào bảng database và trade-off của index là gì',
        intent: 'kiểm tra hiểu biết hiệu năng database dựa trên query pattern thay vì thêm index cảm tính',
        guidance: 'Nêu query hay dùng, EXPLAIN plan, read/write trade-off, storage cost và cách đo trước/sau.',
    },
    {
        slug: 'transaction-consistency',
        category: 'Database / SQL',
        role: 'Backend Developer',
        tags: ['transaction', 'consistency', 'ACID'],
        prompt: 'Bạn dùng transaction để tránh dữ liệu không nhất quán trong flow nhiều bảng như thế nào',
        intent: 'kiểm tra khả năng bảo vệ dữ liệu khi một phần thao tác thất bại',
        guidance: 'Dùng ví dụ tạo session + transcript + report, giải thích commit/rollback, isolation và lỗi cần retry.',
    },
    {
        slug: 'fastapi-validation',
        category: 'FastAPI',
        role: 'Backend Developer',
        tags: ['FastAPI', 'Pydantic', 'validation'],
        prompt: 'Trong FastAPI, bạn sẽ validate request và trả lỗi rõ ràng cho client như thế nào',
        intent: 'kiểm tra hiểu biết schema, status code và hợp đồng API',
        guidance: 'Nêu Pydantic model, validator, giới hạn field, HTTPException có detail hữu ích và test lỗi biên.',
    },
    {
        slug: 'node-event-loop',
        category: 'Node.js',
        role: 'Backend Developer',
        tags: ['Node.js', 'event loop', 'scalability'],
        prompt: 'Nếu backend Node.js bị chậm do tác vụ CPU-heavy, bạn sẽ xử lý như thế nào',
        intent: 'kiểm tra hiểu biết event loop và cách tách workload phù hợp',
        guidance: 'Nêu đo bottleneck, worker thread/job queue, cache, phân trang, tránh block event loop và monitoring.',
    },
    {
        slug: 'system-design-job-alert',
        category: 'System Design',
        role: 'Backend Developer',
        tags: ['system design', 'job alert', 'queue'],
        prompt: 'Thiết kế hệ thống gửi job alert cho ứng viên quan tâm vị trí IT phù hợp với CV',
        intent: 'kiểm tra khả năng xác định yêu cầu, mô hình dữ liệu, matching, queue và chống gửi trùng',
        guidance: 'Làm rõ scale, preferences, job index, matching job, queue email, deduplication và observability.',
    },
    {
        slug: 'system-design-interview-platform',
        category: 'System Design',
        role: 'Fullstack Developer',
        tags: ['system design', 'interview', 'real-time'],
        prompt: 'Thiết kế MVP cho nền tảng phỏng vấn giọng nói có transcript và báo cáo AI',
        intent: 'kiểm tra tư duy end-to-end từ realtime audio đến lưu trữ và đánh giá',
        guidance: 'Nêu client, WebSocket, STT, LLM/TTS, lưu transcript, report async, bảo mật session và fallback.',
    },
    {
        slug: 'fullstack-upload-flow',
        category: 'Fullstack',
        role: 'Fullstack Developer',
        tags: ['file upload', 'API', 'UX'],
        prompt: 'Bạn thiết kế flow upload CV từ frontend đến backend như thế nào để an toàn và dễ dùng',
        intent: 'kiểm tra phối hợp UX, API, validation file, trạng thái xử lý và lỗi',
        guidance: 'Nêu validate client/server, multipart, size/type, progress/loading, retry, virus scan nếu cần và lưu metadata.',
    },
    {
        slug: 'fullstack-state-sync',
        category: 'Fullstack',
        role: 'Fullstack Developer',
        tags: ['state sync', 'API', 'consistency'],
        prompt: 'Khi frontend hiển thị dữ liệu vừa được backend xử lý async, bạn đồng bộ trạng thái như thế nào',
        intent: 'kiểm tra khả năng thiết kế UI cho tác vụ không tức thời',
        guidance: 'Nêu polling/WebSocket, status field, optimistic UI thận trọng, retry và empty/loading/error state.',
    },
    {
        slug: 'testing-login',
        category: 'Testing / QA',
        role: 'QA Engineer',
        tags: ['test plan', 'auth', 'edge cases'],
        prompt: 'Lập test plan cho chức năng login/signup trong một ứng dụng SaaS',
        intent: 'kiểm tra tư duy test theo rủi ro, không chỉ happy path',
        guidance: 'Nêu case hợp lệ, input sai, session expired, rate limit, accessibility, cross-browser và security cơ bản.',
    },
    {
        slug: 'qa-automation-selection',
        category: 'Testing / QA',
        role: 'QA Engineer',
        tags: ['automation', 'regression', 'priority'],
        prompt: 'Bạn chọn test case nào để automation trước khi release một dashboard quản lý ứng viên',
        intent: 'kiểm tra khả năng ưu tiên automation dựa trên giá trị và độ ổn định',
        guidance: 'Ưu tiên flow critical, regression cao, ít thay đổi UI, dữ liệu kiểm soát được và báo cáo lỗi rõ.',
    },
    {
        slug: 'devops-cicd',
        category: 'DevOps',
        role: 'DevOps Engineer',
        tags: ['CI/CD', 'pipeline', 'deployment'],
        prompt: 'Một pipeline CI/CD cơ bản cho React + FastAPI nên gồm những bước nào',
        intent: 'kiểm tra hiểu biết build, test, container, config và rollback',
        guidance: 'Nêu install, lint/test/build, Docker image, env/secrets, migration, deploy, health check và rollback.',
    },
    {
        slug: 'docker-debug',
        category: 'Docker / Deployment',
        role: 'DevOps Engineer',
        tags: ['Docker', 'deployment', 'debug'],
        prompt: 'Container chạy được ở local nhưng fail trên server, bạn sẽ debug theo thứ tự nào',
        intent: 'kiểm tra khả năng xử lý môi trường, network, biến môi trường và log',
        guidance: 'Nêu image tag, env vars, port, volume, network, healthcheck, logs, resource limit và khác biệt kiến trúc.',
    },
    {
        slug: 'cloud-cost-reliability',
        category: 'Cloud Basics',
        role: 'DevOps Engineer',
        tags: ['cloud', 'cost', 'reliability'],
        prompt: 'Khi deploy một API lên cloud, bạn cân bằng chi phí, độ tin cậy và khả năng scale như thế nào',
        intent: 'kiểm tra tư duy vận hành thực tế thay vì chỉ biết tên dịch vụ cloud',
        guidance: 'Nêu traffic, autoscaling, managed service, monitoring, backup, budget alert và lựa chọn MVP trước.',
    },
    {
        slug: 'data-sql-cohort',
        category: 'Data Analyst',
        role: 'Data Analyst',
        tags: ['SQL', 'cohort', 'retention'],
        prompt: 'Bạn sẽ phân tích retention theo cohort tuần bằng SQL như thế nào',
        intent: 'kiểm tra định nghĩa metric, cohort và tư duy truy vấn dữ liệu',
        guidance: 'Nêu active user, cohort date, join activity theo tuần, count distinct user và diễn giải trend.',
    },
    {
        slug: 'data-dashboard-metric',
        category: 'Data Analyst',
        role: 'Data Analyst',
        tags: ['dashboard', 'metric', 'stakeholder'],
        prompt: 'Khi stakeholder yêu cầu dashboard nhưng chưa rõ metric, bạn sẽ làm rõ yêu cầu như thế nào',
        intent: 'kiểm tra giao tiếp business, định nghĩa metric và tránh dashboard vô nghĩa',
        guidance: 'Hỏi mục tiêu quyết định, người dùng, định nghĩa số liệu, nguồn dữ liệu, tần suất và ngưỡng hành động.',
    },
    {
        slug: 'data-science-evaluation',
        category: 'Data Science',
        role: 'Data Scientist',
        tags: ['model evaluation', 'dataset', 'metrics'],
        prompt: 'Bạn đánh giá một mô hình phân loại có mất cân bằng dữ liệu như thế nào',
        intent: 'kiểm tra hiểu biết metric phù hợp và phân tích lỗi mô hình',
        guidance: 'Nêu precision/recall/F1/PR-AUC, confusion matrix, threshold, stratified split và cost của false positive/negative.',
    },
    {
        slug: 'ml-resume-parser',
        category: 'AI / Machine Learning',
        role: 'AI Engineer',
        tags: ['LLM', 'evaluation', 'resume parser'],
        prompt: 'Bạn đánh giá độ tin cậy của một AI resume parser như thế nào',
        intent: 'kiểm tra tư duy evaluation, labeled dataset và human review loop',
        guidance: 'Nêu field cần trích, ground truth, exact/partial match, failure taxonomy, regression set và ngưỡng human review.',
    },
    {
        slug: 'ml-hallucination',
        category: 'AI / Machine Learning',
        role: 'AI Engineer',
        tags: ['LLM', 'hallucination', 'guardrails'],
        prompt: 'Nếu LLM tạo nhận xét không có bằng chứng từ CV hoặc transcript, bạn sẽ giảm hallucination thế nào',
        intent: 'kiểm tra khả năng thiết kế prompt, grounding và kiểm chứng đầu ra',
        guidance: 'Nêu evidence citation, JSON schema, retrieval context, refusal rules, post-validation và human review.',
    },
    {
        slug: 'python-performance',
        category: 'Python',
        role: 'Backend Developer',
        tags: ['Python', 'performance', 'profiling'],
        prompt: 'Bạn từng tối ưu một đoạn Python chậm như thế nào, đo nguyên nhân và kết quả ra sao',
        intent: 'kiểm tra tư duy profiling và cải thiện có đo lường',
        guidance: 'Nêu profiler/log timing, nguyên nhân, thuật toán/data structure/cache/batch I/O và số liệu trước sau.',
    },
    {
        slug: 'python-async',
        category: 'Python',
        role: 'Backend Developer',
        tags: ['Python', 'async', 'I/O'],
        prompt: 'Khi nào bạn dùng async trong Python backend và lỗi thường gặp khi dùng async là gì',
        intent: 'kiểm tra hiểu biết I/O-bound, event loop và tránh blocking call',
        guidance: 'Nêu HTTP/DB I/O, await đầy đủ, không block event loop, connection pool và timeout.',
    },
    {
        slug: 'security-idor',
        category: 'Security Basics',
        role: 'Backend Developer',
        tags: ['security', 'IDOR', 'authorization'],
        prompt: 'Làm sao để tránh lỗi người dùng truy cập được CV hoặc report của người khác qua ID trên URL',
        intent: 'kiểm tra authorization theo owner/resource và rủi ro IDOR',
        guidance: 'Nêu kiểm tra user_id ở query, không tin client, test cross-user, audit log và response 404/403 phù hợp.',
    },
    {
        slug: 'security-secrets',
        category: 'Security Basics',
        role: 'DevOps Engineer',
        tags: ['secrets', 'environment', 'deployment'],
        prompt: 'Bạn quản lý secrets như API key, database password trong môi trường dev/staging/prod như thế nào',
        intent: 'kiểm tra nhận thức bảo mật vận hành',
        guidance: 'Nêu env vars/secret manager, phân quyền, rotate, không commit, audit access và fallback local an toàn.',
    },
    {
        slug: 'performance-api-db',
        category: 'Performance / Optimization',
        role: 'Backend Developer',
        tags: ['API performance', 'database', 'cache'],
        prompt: 'Bạn đã từng tối ưu hiệu năng API hoặc truy vấn database như thế nào? Hãy mô tả cách đo, nguyên nhân và kết quả',
        intent: 'kiểm tra khả năng tối ưu dựa trên bằng chứng thay vì đoán',
        guidance: 'Nêu metric latency/throughput, log slow query, index, pagination, cache, batch query và số liệu cải thiện.',
    },
    {
        slug: 'performance-frontend',
        category: 'Performance / Optimization',
        role: 'Frontend Developer',
        tags: ['frontend performance', 'bundle', 'render'],
        prompt: 'Bạn cải thiện tốc độ tải hoặc tương tác của một trang React như thế nào',
        intent: 'kiểm tra hiểu biết bundle, lazy loading, render cost và đo Web Vitals',
        guidance: 'Nêu đo Lighthouse/Profiler, code splitting, defer asset, cache, giảm re-render và kiểm tra thiết bị yếu.',
    },
    {
        slug: 'git-branching',
        category: 'Git / Teamwork',
        role: 'Fullstack Developer',
        tags: ['Git', 'branching', 'release'],
        prompt: 'Bạn tổ chức branch, pull request và release như thế nào để giảm conflict và lỗi deploy',
        intent: 'kiểm tra quy trình làm việc nhóm',
        guidance: 'Nêu branch nhỏ, PR review, CI, rebase/merge strategy, feature flag và release checklist.',
    },
    {
        slug: 'mobile-offline-sync',
        category: 'Fullstack',
        role: 'Mobile Developer',
        tags: ['mobile', 'offline sync', 'conflict'],
        prompt: 'Nếu ứng dụng mobile cần dùng offline rồi đồng bộ lại, bạn thiết kế xử lý conflict như thế nào',
        intent: 'kiểm tra tư duy dữ liệu phân tán và UX khi đồng bộ lỗi',
        guidance: 'Nêu local queue, timestamp/version, conflict policy, retry/backoff, thông báo cho user và audit.',
    },
    {
        slug: 'intern-fundamental-api',
        category: 'Intern / Fresher fundamentals',
        role: 'Software Engineer Intern',
        tags: ['fundamental', 'API', 'client-server'],
        prompt: 'Khi frontend gọi API và nhận lỗi 400, 401, 500, bạn hiểu và xử lý từng nhóm lỗi ra sao',
        intent: 'kiểm tra nền tảng client-server và cách xử lý lỗi người dùng',
        guidance: 'Nêu ý nghĩa từng status, ví dụ UI message, retry khi phù hợp và log/report lỗi server.',
    },
    {
        slug: 'junior-estimation',
        category: 'Junior problem solving',
        role: 'Fresher Software Engineer',
        tags: ['estimation', 'planning', 'risk'],
        prompt: 'Khi được giao một task chưa rõ yêu cầu, bạn sẽ hỏi gì trước khi estimate và bắt đầu làm',
        intent: 'kiểm tra khả năng làm rõ yêu cầu và tránh làm sai hướng',
        guidance: 'Hỏi mục tiêu, acceptance criteria, dữ liệu, edge case, ưu tiên, deadline và rủi ro phụ thuộc.',
    },
    {
        slug: 'senior-architecture-tradeoff',
        category: 'Middle/Senior architecture thinking',
        role: 'Backend Developer',
        tags: ['architecture', 'trade-off', 'scalability'],
        prompt: 'Bạn chọn giữa monolith module hóa và microservices như thế nào cho một sản phẩm đang tăng trưởng',
        intent: 'kiểm tra tư duy kiến trúc dựa trên bối cảnh thay vì chạy theo xu hướng',
        guidance: 'Nêu team size, domain boundary, deploy frequency, data ownership, observability, chi phí vận hành và migration path.',
    },
    {
        slug: 'senior-observability',
        category: 'Middle/Senior architecture thinking',
        role: 'DevOps Engineer',
        tags: ['observability', 'SLO', 'incident'],
        prompt: 'Bạn thiết kế logging, metrics và alerting cho một dịch vụ quan trọng như thế nào',
        intent: 'kiểm tra khả năng vận hành production và phản ứng sự cố',
        guidance: 'Nêu RED/USE metrics, structured logs, trace id, alert theo symptom, dashboard SLO và runbook.',
    },
    {
        slug: 'backend-rate-limit',
        category: 'Backend',
        role: 'Backend Developer',
        tags: ['rate limit', 'abuse prevention', 'API'],
        prompt: 'Bạn thêm rate limiting cho API đăng nhập hoặc matching như thế nào để vừa an toàn vừa không gây khó chịu',
        intent: 'kiểm tra cân bằng bảo mật, UX và vận hành',
        guidance: 'Nêu key theo IP/user, window, message rõ, allowlist nội bộ, monitoring false positive và retry-after.',
    },
    {
        slug: 'frontend-design-system',
        category: 'Frontend',
        role: 'Frontend Developer',
        tags: ['design system', 'components', 'consistency'],
        prompt: 'Khi nhiều page dùng card, button, form khác nhau không nhất quán, bạn sẽ chuẩn hóa frontend như thế nào',
        intent: 'kiểm tra khả năng làm frontend có hệ thống',
        guidance: 'Nêu token, component primitive, variant rõ ràng, audit usage, migration từng page và regression visual.',
    },
    {
        slug: 'backend-background-job',
        category: 'Backend',
        role: 'Backend Developer',
        tags: ['Celery', 'background job', 'retry'],
        prompt: 'Khi một tác vụ crawl hoặc AI evaluation chạy lâu, bạn thiết kế background job và retry như thế nào',
        intent: 'kiểm tra tư duy async processing, idempotency và quan sát lỗi',
        guidance: 'Nêu queue, task idempotent, retry/backoff, timeout, status tracking, dead letter và log có correlation id.',
    },
    {
        slug: 'crawler-ethics',
        category: 'Backend',
        role: 'Backend Developer',
        tags: ['crawler', 'rate limit', 'ethics'],
        prompt: 'Khi xây crawler lấy job public, bạn làm gì để crawler an toàn và tôn trọng website nguồn',
        intent: 'kiểm tra nhận thức đạo đức/kỹ thuật về crawling',
        guidance: 'Nêu robots/terms, user-agent rõ, rate limit thấp, không bypass CAPTCHA/login, timeout, retry giới hạn và fallback minh bạch.',
    },
    {
        slug: 'api-contract-change',
        category: 'Fullstack',
        role: 'Fullstack Developer',
        tags: ['API contract', 'compatibility', 'frontend-backend'],
        prompt: 'Nếu cần thêm field mới vào API đang được frontend dùng, bạn làm sao để không làm gãy client cũ',
        intent: 'kiểm tra tư duy tương thích ngược',
        guidance: 'Nêu optional field, default value, versioning khi cần, contract test, rollout từng bước và logging client error.',
    },
    {
        slug: 'job-matching-score',
        category: 'Job Description-based Questions',
        role: 'Data Scientist',
        tags: ['matching', 'scoring', 'evaluation'],
        prompt: 'Bạn sẽ giải thích và kiểm chứng một điểm match CV-JD để người dùng tin được như thế nào',
        intent: 'kiểm tra khả năng kết hợp model, rule-based score và giải thích sản phẩm',
        guidance: 'Nêu thành phần score, evidence từ CV/JD, missing skills, calibration bằng dữ liệu thật và human review.',
    },
    {
        slug: 'sql-window-function',
        category: 'Database / SQL',
        role: 'Data Analyst',
        tags: ['SQL', 'window function', 'analytics'],
        prompt: 'Bạn dùng window function để giải bài toán phân tích ranking hoặc rolling metric như thế nào',
        intent: 'kiểm tra SQL phân tích thực tế',
        guidance: 'Nêu partition/order, rank/row_number, moving average, edge case null và kiểm tra kết quả bằng sample nhỏ.',
    },
    {
        slug: 'react-state-url',
        category: 'React',
        role: 'Frontend Developer',
        tags: ['React', 'state', 'URL params'],
        prompt: 'Khi filter của danh sách cần share được qua URL, bạn quản lý state giữa component và query params ra sao',
        intent: 'kiểm tra UX state persistence và routing',
        guidance: 'Nêu nguồn sự thật, debounce search, sync URL an toàn, default value và tránh loop update.',
    },
    {
        slug: 'fastapi-db-session',
        category: 'FastAPI',
        role: 'Backend Developer',
        tags: ['FastAPI', 'SQLAlchemy', 'session'],
        prompt: 'Bạn quản lý database session trong FastAPI async để tránh leak connection như thế nào',
        intent: 'kiểm tra kiến thức dependency, transaction và connection pool',
        guidance: 'Nêu dependency session per request, commit/rollback rõ, close session, không giữ ORM object ngoài scope và pool metrics.',
    },
    {
        slug: 'devops-migration',
        category: 'Docker / Deployment',
        role: 'DevOps Engineer',
        tags: ['migration', 'deployment', 'rollback'],
        prompt: 'Bạn chạy database migration trong pipeline deploy như thế nào để giảm rủi ro downtime',
        intent: 'kiểm tra tư duy deploy an toàn với schema change',
        guidance: 'Nêu backward-compatible migration, backup, expand/contract, migration trước code khi an toàn, rollback plan và smoke test.',
    },
    {
        slug: 'qa-flaky-test',
        category: 'Testing / QA',
        role: 'QA Engineer',
        tags: ['flaky test', 'automation', 'CI'],
        prompt: 'Nếu test automation thỉnh thoảng fail trên CI nhưng pass local, bạn điều tra như thế nào',
        intent: 'kiểm tra debugging test và ổn định pipeline',
        guidance: 'Nêu screenshot/video/log, timing/wait, data isolation, network mock, retry tạm thời có cảnh báo và fix nguyên nhân.',
    },
    {
        slug: 'ai-data-privacy',
        category: 'AI / Machine Learning',
        role: 'AI Engineer',
        tags: ['privacy', 'AI', 'PII'],
        prompt: 'Khi gửi CV hoặc transcript vào mô hình AI, bạn bảo vệ dữ liệu cá nhân như thế nào',
        intent: 'kiểm tra nhận thức bảo mật dữ liệu trong sản phẩm AI',
        guidance: 'Nêu minimization, masking PII khi phù hợp, consent, retention, access control, audit và provider policy.',
    },
    {
        slug: 'backend-pagination',
        category: 'REST API',
        role: 'Backend Developer',
        tags: ['pagination', 'filter', 'API'],
        prompt: 'Bạn thiết kế pagination và filter cho endpoint danh sách job như thế nào để ổn định khi dữ liệu tăng',
        intent: 'kiểm tra API list design và hiệu năng',
        guidance: 'Nêu limit max, cursor/offset trade-off, index theo filter, sort ổn định, response metadata và validation query.',
    },
    {
        slug: 'frontend-empty-state',
        category: 'Frontend',
        role: 'Frontend Developer',
        tags: ['empty state', 'UX', 'loading'],
        prompt: 'Bạn thiết kế loading, empty và error state cho trang job matching như thế nào để người dùng không bị kẹt',
        intent: 'kiểm tra UX cho trạng thái dữ liệu không hoàn hảo',
        guidance: 'Nêu skeleton/loading, empty có action, error có retry, phân biệt no data và no permission, không che mất thao tác chính.',
    },
    {
        slug: 'senior-mentoring',
        category: 'Behavioral',
        role: 'Backend Developer',
        tags: ['mentoring', 'leadership', 'code quality'],
        prompt: 'Bạn đã từng giúp một thành viên khác cải thiện chất lượng code hoặc cách debug như thế nào',
        intent: 'kiểm tra năng lực mentoring và ảnh hưởng tích cực đến team',
        guidance: 'Nêu bối cảnh, cách hướng dẫn, công cụ/checklist, tiến bộ đo được và điều bạn học được.',
    },
    {
        slug: 'product-technical-tradeoff',
        category: 'Middle/Senior architecture thinking',
        role: 'Fullstack Developer',
        tags: ['product thinking', 'trade-off', 'MVP'],
        prompt: 'Khi product muốn ra mắt nhanh nhưng giải pháp kỹ thuật chưa hoàn hảo, bạn trao đổi trade-off như thế nào',
        intent: 'kiểm tra tư duy sản phẩm, quản trị nợ kỹ thuật và giao tiếp với stakeholder',
        guidance: 'Nêu rủi ro, phương án MVP, guardrail, thời hạn trả nợ kỹ thuật, metric theo dõi và quyết định chung.',
    },
];

function slugify(value) {
    return value
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '');
}

function themeKind(theme) {
    const text = `${theme.category} ${theme.tags.join(' ')} ${theme.slug}`.toLowerCase();
    if (text.includes('system design') || text.includes('architecture')) return 'architecture';
    if (text.includes('debug') || text.includes('bug') || text.includes('performance') || text.includes('testing') || text.includes('qa')) return 'debug';
    if (text.includes('data') || text.includes('machine learning') || text.includes('ai')) return 'data';
    if (text.includes('security') || text.includes('auth') || text.includes('api') || text.includes('database') || text.includes('sql')) return 'concept';
    if (text.includes('behavioral') || text.includes('teamwork') || text.includes('conflict') || text.includes('mentoring')) return 'behavioral';
    if (text.includes('project') || text.includes('cv-based') || text.includes('job description')) return 'evidence';
    if (text.includes('hr') || text.includes('general') || text.includes('career')) return 'intro';
    return 'technical';
}

function answerStructureForTheme(theme) {
    const kind = themeKind(theme);
    if (kind === 'architecture') {
        return [
            'Làm rõ yêu cầu: scope, user, dữ liệu, SLA, bảo mật và ràng buộc triển khai.',
            'Đề xuất thiết kế: component chính, data flow, API hoặc storage cần dùng.',
            'Nêu trade-off: vì sao chọn hướng này thay vì phương án khác.',
            'Kiểm chứng: metric, logging, test, rollback hoặc cách vận hành sau khi release.',
        ];
    }
    if (kind === 'debug') {
        return [
            'Khoanh vùng triệu chứng: lỗi xảy ra ở đâu, tần suất, input và môi trường liên quan.',
            'Thu thập bằng chứng: log, metric, profiler, screenshot, test case hoặc dữ liệu mẫu.',
            'Xử lý có kiểm soát: fix nhỏ, giảm rủi ro cho user và tránh làm rộng phạm vi lỗi.',
            'Xác nhận kết quả: test lại, theo dõi sau deploy và ghi lại bài học để tránh lặp lại.',
        ];
    }
    if (kind === 'concept') {
        return [
            'Định nghĩa ngắn gọn bằng ngôn ngữ dễ hiểu.',
            'Đưa ví dụ thực tế từ endpoint, database, auth flow hoặc hệ thống đã làm.',
            'Nêu rủi ro/trade-off nếu áp dụng sai hoặc thiếu kiểm soát.',
            'Kết lại bằng cách bạn kiểm chứng hoặc triển khai trong production.',
        ];
    }
    if (kind === 'data') {
        return [
            'Xác định bài toán, metric hoặc giả thuyết cần kiểm chứng.',
            'Nêu nguồn dữ liệu, bước xử lý, feature hoặc model/rule được dùng.',
            'Giải thích cách đánh giá: baseline, validation, error analysis hoặc business metric.',
            'Kết luận bằng quyết định sản phẩm/kỹ thuật rút ra từ kết quả.',
        ];
    }
    if (kind === 'behavioral') {
        return [
            'Mở bằng tình huống thật và mục tiêu chung của team.',
            'Nêu nguyên tắc xử lý: lắng nghe, dùng dữ liệu, tách vấn đề khỏi cá nhân.',
            'Kể hành động cụ thể bạn làm và cách phối hợp với người liên quan.',
            'Kết quả, bài học và thay đổi trong cách làm việc sau đó.',
        ];
    }
    if (kind === 'intro') {
        return [
            'Tóm tắt nền tảng, vai trò mục tiêu và lý do phù hợp.',
            'Chọn 2-3 kỹ năng hoặc project liên quan nhất đến vị trí.',
            'Nêu bằng chứng cụ thể thay vì liệt kê quá nhiều công nghệ.',
            'Kết thúc bằng mục tiêu gần và giá trị bạn muốn đóng góp.',
        ];
    }
    if (kind === 'evidence') {
        return [
            'Chọn ví dụ sát CV/JD nhất và nêu bối cảnh đủ ngắn.',
            'Làm rõ phần bạn trực tiếp phụ trách, quyết định kỹ thuật và phạm vi ảnh hưởng.',
            'Nêu khó khăn, trade-off hoặc thứ bạn đã phải học để xử lý.',
            'Kết quả: số liệu nếu có, feedback, artifact hoặc bài học đáng tin cậy.',
        ];
    }
    return [
        'Trả lời thẳng vào trọng tâm bằng khái niệm hoặc hướng xử lý chính.',
        'Minh họa bằng một ví dụ thực tế trong code, project hoặc workflow.',
        'Nêu edge case, trade-off hoặc lỗi thường gặp liên quan.',
        'Kết lại bằng cách kiểm tra chất lượng: test, review, log hoặc metric.',
    ];
}

function sampleAnswerForTheme(theme, context) {
    const kind = themeKind(theme);
    if (kind === 'architecture') {
        return `Tôi sẽ bắt đầu bằng việc làm rõ yêu cầu chính, quy mô dữ liệu và ràng buộc vận hành. Sau đó tôi đề xuất thiết kế gồm các thành phần chính, luồng dữ liệu, API và storage, rồi so sánh trade-off giữa tốc độ triển khai, khả năng mở rộng và độ phức tạp. Cuối cùng tôi xác nhận bằng test, logging, metric theo dõi và kế hoạch rollback nếu release có rủi ro.`;
    }
    if (kind === 'debug') {
        return `Tôi sẽ khoanh vùng lỗi trước bằng log, metric và input cụ thể thay vì sửa theo cảm tính. Khi có giả thuyết, tôi tạo case nhỏ để tái hiện hoặc so sánh giữa môi trường local và production, sau đó triển khai fix có phạm vi hẹp. Sau khi sửa, tôi kiểm tra lại bằng test, theo dõi metric sau deploy và ghi lại nguyên nhân để tránh lỗi lặp lại.`;
    }
    if (kind === 'concept') {
        return `Tôi hiểu vấn đề này theo hướng thực tế: trước hết cần nắm đúng khái niệm, sau đó áp dụng vào một flow cụ thể như API, database hoặc phân quyền. Điểm quan trọng là không chỉ làm cho chạy được mà còn kiểm soát edge case, lỗi đầu vào, quyền truy cập và khả năng quan sát khi có sự cố.`;
    }
    if (kind === 'data') {
        return `Tôi sẽ xác định metric cần tối ưu trước, sau đó kiểm tra nguồn dữ liệu và chất lượng dữ liệu. Với phân tích hoặc model, tôi luôn so với baseline, xem lỗi ở các nhóm dữ liệu khác nhau và chỉ kết luận khi kết quả có ý nghĩa với quyết định sản phẩm hoặc vận hành.`;
    }
    if (kind === 'behavioral') {
        return `Trong ${context.scope}, tôi từng gặp tình huống liên quan đến ${theme.tags[0]}. Tôi trao đổi thẳng vào mục tiêu chung, đưa ra dữ liệu hoặc ví dụ cụ thể, lắng nghe quan điểm khác và thống nhất một hướng thử nghiệm nhỏ. Kết quả là team giảm tranh luận cảm tính, có căn cứ để quyết định và tôi học được cách phản hồi rõ ràng hơn.`;
    }
    if (kind === 'intro') {
        return `Tôi có nền tảng phù hợp với hướng ${theme.role}, đặc biệt ở ${theme.tags.slice(0, 2).join(' và ')}. Trong ${context.scope}, tôi đã có ${context.evidence}, qua đó rèn cách phân tích yêu cầu, triển khai có kiểm chứng và trình bày kết quả rõ ràng. Mục tiêu gần của tôi là tham gia vào sản phẩm thật, học nhanh từ review và đóng góp ổn định cho team.`;
    }
    if (kind === 'evidence') {
        return `Trong ${context.scope}, ví dụ rõ nhất của tôi là một phần việc liên quan đến ${theme.tags[0]}. Tôi phụ trách phân tích yêu cầu, triển khai phần lõi trong phạm vi của mình và phối hợp với team khi có điểm chưa rõ. Kết quả được kiểm chứng bằng test, phản hồi hoặc artifact cụ thể, và tôi rút ra bài học về cách làm rõ scope trước khi code.`;
    }
    return `Tôi sẽ trả lời bằng cách đi từ nguyên lý chính đến ví dụ thực tế. Với ${theme.tags[0]}, tôi thường nêu cách áp dụng trong project, các edge case cần chú ý và cách kiểm tra bằng test hoặc log. Như vậy câu trả lời không chỉ là lý thuyết mà cho thấy tôi biết dùng kiến thức đó trong công việc.`;
}

function buildQuestion(theme, level) {
    const context = LEVEL_CONTEXT[level];
    const id = `${theme.slug}-${slugify(level)}`;
    const question = `${theme.prompt} ${context.scope}? Hãy nêu ${context.evidence}, cách bạn xử lý và kết quả.`;
    const structure = answerStructureForTheme(theme);
    const mistakes = [
        'Trả lời quá lý thuyết, không có ví dụ cụ thể.',
        'Không nói rõ vai trò cá nhân hoặc mức độ đóng góp.',
        'Bỏ qua lỗi, rủi ro, trade-off hoặc cách đo kết quả.',
    ];
    const sample = sampleAnswerForTheme(theme, context);

    return {
        id,
        question_vi: question,
        question,
        category: theme.category,
        role: theme.role,
        level,
        difficulty: context.difficulty,
        tags: [...theme.tags, level],
        interviewer_expectation_vi: `${theme.intent}; ở level ${level}, ${context.expectation}.`,
        expectations: `${theme.intent}; ở level ${level}, ${context.expectation}.`,
        suggested_answer_structure_vi: structure,
        answerStructure: structure,
        common_mistakes_vi: mistakes,
        commonMistakes: mistakes,
        sample_answer_vi: sample,
        sampleAnswer: sample,
        answer_guidance_vi: theme.guidance,
        starHint: theme.guidance,
    };
}

export const QUESTION_BANK = QUESTION_THEMES.flatMap((theme) =>
    IT_LEVELS.map((level) => buildQuestion(theme, level))
);

export function allQuestionTags() {
    return [...new Set(QUESTION_BANK.flatMap((item) => item.tags || []))].sort();
}
