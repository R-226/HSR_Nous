"""Tests for sim_schema.actor module."""

import pytest

from hsr_nous.sim_schema.actor import Actor, StatBlock


class TestStatBlock:
    """StatBlock 数据类测试."""

    def test_default_construction(self):
        """StatBlock 默认构造应返回预设的基础值."""
        sb = StatBlock()

        assert sb.hp == 0.0
        assert sb.atk == 0.0
        assert sb.def_ == 0.0
        assert sb.spd == 100.0
        assert sb.crit_rate == 0.05
        assert sb.crit_dmg == 0.50
        assert sb.break_effect == 0.0
        assert sb.effect_hit == 0.0
        assert sb.effect_res == 0.0
        assert sb.max_energy == 0.0
        assert sb.energy == 0.0
        assert sb.energy_regen == 1.0
        assert sb.heal_bonus == 0.0
        assert sb.shield_bonus == 0.0
        assert sb.dmg_bonus == {}
        assert sb.resistance == {}
        assert sb.weakness == []
        assert sb.taunt == 100.0
        assert sb.elation == 0.0
        assert sb.max_toughness == 0.0
        assert sb.toughness == 0.0
        assert sb.follow_up_dmg_bonus == 0.0

    def test_custom_values(self):
        """StatBlock 应支持自定义属性值."""
        sb = StatBlock(
            hp=5000.0,
            atk=1200.0,
            def_=800.0,
            spd=115.0,
            crit_rate=0.60,
            crit_dmg=1.20,
            break_effect=0.30,
            effect_hit=0.40,
            effect_res=0.20,
            max_energy=120.0,
            energy=60.0,
            energy_regen=1.2,
            heal_bonus=0.15,
            shield_bonus=0.10,
            dmg_bonus={"physical": 0.1, "fire": 0.2, "all": 0.05},
            resistance={"physical": 0.2, "fire": 0.0},
            weakness=["fire", "ice"],
            taunt=150.0,
            elation=10.0,
            max_toughness=120.0,
            toughness=120.0,
            follow_up_dmg_bonus=0.25,
        )

        assert sb.hp == 5000.0
        assert sb.atk == 1200.0
        assert sb.def_ == 800.0
        assert sb.spd == 115.0
        assert sb.crit_rate == 0.60
        assert sb.crit_dmg == 1.20
        assert sb.break_effect == 0.30
        assert sb.effect_hit == 0.40
        assert sb.effect_res == 0.20
        assert sb.max_energy == 120.0
        assert sb.energy == 60.0
        assert sb.energy_regen == 1.2
        assert sb.heal_bonus == 0.15
        assert sb.shield_bonus == 0.10
        assert sb.dmg_bonus == {"physical": 0.1, "fire": 0.2, "all": 0.05}
        assert sb.resistance == {"physical": 0.2, "fire": 0.0}
        assert sb.weakness == ["fire", "ice"]
        assert sb.taunt == 150.0
        assert sb.elation == 10.0
        assert sb.max_toughness == 120.0
        assert sb.toughness == 120.0
        assert sb.follow_up_dmg_bonus == 0.25


class TestActor:
    """Actor 数据类测试."""

    def test_default_construction(self):
        """Actor 最小构造（仅必填字段）."""
        actor = Actor(actor_id="test_001", name="TestActor")

        assert actor.actor_id == "test_001"
        assert actor.name == "TestActor"
        assert actor.actor_type == "character"
        assert actor.level == 80
        assert isinstance(actor.stats, StatBlock)
        assert actor.actions == []
        assert actor.modifiers == []
        assert actor.max_hp == 0.0
        assert actor.active_modifiers == []
        assert actor.current_av == 0.0
        assert actor.base_av == 0.0
        assert actor.owner_id is None

    def test_actor_with_all_new_fields(self):
        """Actor 应支持所有新增字段的自定义赋值."""
        actor = Actor(
            actor_id="char_kafka",
            name="Kafka",
            actor_type="character",
            level=80,
            stats=StatBlock(spd=120.0, atk=3500.0),
            actions=["skill", "basic_atk", "ultimate"],
            modifiers=["kafka_dot", "kafka_talent"],
            max_hp=8000.0,
            active_modifiers=["kafka_dot"],
            current_av=5000.0,
            base_av=83.33,
            owner_id=None,
        )

        assert actor.actor_id == "char_kafka"
        assert actor.name == "Kafka"
        assert actor.max_hp == 8000.0
        assert actor.active_modifiers == ["kafka_dot"]
        assert actor.current_av == 5000.0
        assert pytest.approx(actor.base_av, abs=0.01) == 83.33
        assert actor.owner_id is None
        assert actor.stats.spd == 120.0

    def test_summon_type_with_owner(self):
        """召唤物类型应支持 owner_id 字段."""
        summon = Actor(
            actor_id="summon_lightning_lord",
            name="Lightning Lord",
            actor_type="summon",
            level=80,
            stats=StatBlock(atk=2000.0, spd=0.0),
            max_hp=0.0,
            owner_id="char_jing_yuan",
        )

        assert summon.actor_type == "summon"
        assert summon.owner_id == "char_jing_yuan"
        assert summon.stats.atk == 2000.0
        assert summon.stats.spd == 0.0

    def test_summon_type_without_owner(self):
        """召唤物类型不指定 owner_id 时应为 None."""
        summon = Actor(
            actor_id="summon_test",
            name="Test Summon",
            actor_type="summon",
        )

        assert summon.actor_type == "summon"
        assert summon.owner_id is None

    def test_max_hp_default_zero(self):
        """max_hp 默认值应为 0.0."""
        actor = Actor(actor_id="a1", name="A")
        assert actor.max_hp == 0.0

    def test_current_av_default_zero(self):
        """current_av 和 base_av 默认值应为 0.0."""
        actor = Actor(actor_id="a1", name="A")
        assert actor.current_av == 0.0
        assert actor.base_av == 0.0

    def test_active_modifiers_default_empty(self):
        """active_modifiers 默认应为空列表."""
        actor = Actor(actor_id="a1", name="A")
        assert actor.active_modifiers == []
        # 确认与 modifiers 是独立的列表对象
        assert actor.active_modifiers is not actor.modifiers

    def test_monster_type(self):
        """怪物类型构造应正常工作."""
        monster = Actor(
            actor_id="monster_001",
            name="Cocolia",
            actor_type="monster",
            level=90,
            stats=StatBlock(
                hp=50000.0,
                atk=2500.0,
                def_=1200.0,
                spd=110.0,
                max_toughness=200.0,
                weakness=["fire", "ice", "physical"],
            ),
            max_hp=50000.0,
        )

        assert monster.actor_type == "monster"
        assert monster.level == 90
        assert monster.stats.hp == 50000.0
        assert monster.max_hp == 50000.0
        assert "fire" in monster.stats.weakness
        assert monster.owner_id is None
