## Task 2: Goal → Main AIM(s)

- Mục tiêu: Gắn nhãn 1 hoặc nhiều AIM phù hợp nhất với mục tiêu học ngôn ngữ đầu vào.
- Input: "I want to learn how to give directions to a taxi driver."
- Output: [aim_005, aim_021]

Tiêu chí chọn AIM:
- Liên quan trực tiếp đến mục tiêu
- Đủ nhỏ (atomic) nhưng đủ rõ để dạy riêng
- Ưu tiên AIM có Bloom thấp nếu không rõ trình độ

## Task 3: Main AIMs → Prerequisite AIM Path

- Mục tiêu: Xác định các AIM nền tảng cần học trước cho từng AIM chính.
- Output: [aim_001, aim_003, aim_005]
- Dựa theo quan hệ `preRequisite` trong ontology
