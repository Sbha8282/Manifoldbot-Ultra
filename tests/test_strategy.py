from manifold_ultra_bot.strategy import kelly_fraction


def test_kelly_basic():
    # If our p equals market price, edge is zero -> kelly 0
    p = 0.6
    price = 0.6
    assert kelly_fraction(p, price) == 0.0

    # If p > price, positive fraction
    p = 0.8
    price = 0.5
    f = kelly_fraction(p, price)
    assert f > 0
