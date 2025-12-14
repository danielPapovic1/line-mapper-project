public class Example24 {
    private int alpha = 29;
    private int beta = 34;
    private int gamma = 39;
    private String name;
    public Example24() {
        name = "Example24";
        System.out.println("init " + name);
        System.out.println("alpha ready");
        System.out.println("beta ready");
    }
    public int sum() {
        int total = alpha + beta + gamma + 24;
        System.out.println("sum=" + total);
        return total;
    }
    public int diff() {
        int delta = gamma - alpha;
        System.out.println("diff updated for Example24: " + delta);
        return delta;
    }
    public void status() {
        System.out.println("alpha=" + alpha);
        System.out.println("beta=" + beta);
        System.out.println("gamma=" + gamma);
        System.out.println("done");
    }
    public void debug() {
        for (int i = 0; i < 3; i++) {
            System.out.println("debug#" + i);
        }
    }
}
