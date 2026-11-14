# 노란 공격 방향 화살표 생성 기록

- 사용 도구: 내장 imagegen.
- 참조: `resources/effect_800x400.png`의 하단 방향 화살표.
- 최종 저장: `resources/effect_arrows_yellow.png`.
- 최종 크기: 2172×724px, 투명 배경, 왼쪽·오른쪽·위·아래 순서의 4개 셀.
- 생성 결과의 실제 크기를 사용하며 코드에서 셀 비율을 유지한다. 적 방향 예고용 기존 빨간 시트와 분리했다.

## 최종 생성 프롬프트 원문

```text
Create a simple game UI sprite sheet matching ONLY the four thin flat outline arrows in the BOTTOM ROW of the reference image. Output canvas exact 800x200 (4:1), four equal square cells 200x200. In each cell a small centered FLAT 2D THIN outline arrow: left, right, up, down in that exact order. Outline is uniform pure yellow #FFFF00, thickness about 5px at this canvas size. Each arrow bounding box is 95x95, centered at x=100,300,500,700 y=100. Hollow/empty transparent interior. Fully transparent background. Absolutely NO shadows, NO glow, NO gradients, NO 3D bevel, NO textures, NO solid fill. Just four simple hollow yellow polygon outlines, like a flat minimal arrow key icon, otherwise empty transparent canvas. Do not include the top row of the reference.
```
